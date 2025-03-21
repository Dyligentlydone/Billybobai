from typing import Dict, List, Optional
import asyncio
from datetime import datetime
from enum import Enum
import json

from .twilio_service import TwilioService
from .sendgrid_service import SendGridService
from .zendesk_service import ZendeskService
from ..models.workflow import WorkflowExecution, NodeExecution, ExecutionStatus

class NodeType(Enum):
    TWILIO = "twilio"
    SENDGRID = "sendgrid"
    ZENDESK = "zendesk"
    RESPONSE = "response"

class WorkflowEngine:
    def __init__(self):
        self.twilio_service = TwilioService()
        self.sendgrid_service = SendGridService()
        self.zendesk_service = ZendeskService()
        
    async def execute_workflow(self, workflow_id: str, workflow_data: Dict, input_data: Dict) -> WorkflowExecution:
        """Execute a workflow with the given input data."""
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.utcnow(),
            input_data=input_data,
            node_executions={},
            variables={}
        )
        
        try:
            # Find start nodes (nodes with no incoming edges)
            start_nodes = self._get_start_nodes(workflow_data)
            
            # Execute workflow starting from each start node
            for node in start_nodes:
                await self._execute_node(node, workflow_data, execution)
                
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = datetime.utcnow()
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.end_time = datetime.utcnow()
            execution.error = str(e)
            
        return execution
    
    async def _execute_node(self, node: Dict, workflow_data: Dict, execution: WorkflowExecution) -> None:
        """Execute a single node in the workflow."""
        node_id = node["id"]
        node_type = NodeType(node["type"])
        
        # Create node execution record
        node_execution = NodeExecution(
            node_id=node_id,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        execution.node_executions[node_id] = node_execution
        
        try:
            # Execute node based on type
            result = await self._execute_node_by_type(node_type, node["data"], execution.variables)
            
            # Update variables with node result
            execution.variables[f"node_{node_id}_result"] = result
            
            # Mark node as completed
            node_execution.status = ExecutionStatus.COMPLETED
            node_execution.end_time = datetime.utcnow()
            node_execution.output = result
            
            # Find and execute next nodes
            next_nodes = self._get_next_nodes(node_id, workflow_data)
            for next_node in next_nodes:
                # Check if it's a response node and evaluate conditions
                if next_node["type"] == NodeType.RESPONSE.value:
                    if self._evaluate_response_conditions(next_node["data"], result):
                        await self._execute_node(next_node, workflow_data, execution)
                else:
                    await self._execute_node(next_node, workflow_data, execution)
                    
        except Exception as e:
            node_execution.status = ExecutionStatus.FAILED
            node_execution.end_time = datetime.utcnow()
            node_execution.error = str(e)
            
            # Find error handlers
            error_handlers = self._get_error_handlers(node_id, workflow_data)
            for handler in error_handlers:
                await self._execute_node(handler, workflow_data, execution)
            
            raise
    
    async def _execute_node_by_type(self, node_type: NodeType, node_data: Dict, variables: Dict) -> Dict:
        """Execute a node based on its type."""
        # Replace variables in node data
        node_data = self._replace_variables(node_data, variables)
        
        if node_type == NodeType.TWILIO:
            return await self._execute_twilio_node(node_data)
        elif node_type == NodeType.SENDGRID:
            return await self._execute_sendgrid_node(node_data)
        elif node_type == NodeType.ZENDESK:
            return await self._execute_zendesk_node(node_data)
        elif node_type == NodeType.RESPONSE:
            return await self._execute_response_node(node_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    async def _execute_twilio_node(self, node_data: Dict) -> Dict:
        """Execute a Twilio node."""
        message_type = node_data.get("type", "sms")
        
        if node_data.get("aiModel"):
            # Use AI for message generation
            message = await self.twilio_service.generate_ai_message(
                model=node_data["aiModel"],
                prompt=node_data["prompt"],
                context=node_data.get("context", {})
            )
        else:
            message = node_data["messageTemplate"]
        
        if message_type == "sms":
            result = await self.twilio_service.send_sms(
                to=node_data["to"],
                from_=node_data["phoneNumber"],
                body=message
            )
        elif message_type == "whatsapp":
            result = await self.twilio_service.send_whatsapp(
                to=node_data["to"],
                from_=node_data["phoneNumber"],
                body=message
            )
        elif message_type == "voice":
            result = await self.twilio_service.make_call(
                to=node_data["to"],
                from_=node_data["phoneNumber"],
                twiml=message
            )
        else:
            raise ValueError(f"Unknown Twilio message type: {message_type}")
            
        return result
    
    async def _execute_sendgrid_node(self, node_data: Dict) -> Dict:
        """Execute a SendGrid node."""
        email_type = node_data.get("emailType", "template")
        
        if email_type == "template":
            result = await self.sendgrid_service.send_template_email(
                template_id=node_data["templateId"],
                to=node_data["to"],
                subject=node_data["subject"],
                dynamic_data=node_data.get("dynamicData", {})
            )
        elif email_type == "custom":
            result = await self.sendgrid_service.send_custom_email(
                to=node_data["to"],
                subject=node_data["subject"],
                content=node_data["content"]
            )
        else:
            raise ValueError(f"Unknown SendGrid email type: {email_type}")
            
        return result
    
    async def _execute_zendesk_node(self, node_data: Dict) -> Dict:
        """Execute a Zendesk node."""
        result = await self.zendesk_service.create_ticket(
            subject=node_data["subject"],
            description=node_data.get("description", ""),
            priority=node_data.get("priority", "normal"),
            category=node_data.get("category", "support"),
            assignee=node_data.get("assignee"),
            custom_fields=node_data.get("customFields", {})
        )
        return result
    
    async def _execute_response_node(self, node_data: Dict) -> Dict:
        """Execute a response node."""
        response_type = node_data["responseType"]
        action = node_data["action"]
        
        if action == "retry":
            # Implement retry logic
            max_retries = node_data.get("maxRetries", 3)
            delay = node_data.get("delay", 5)
            return {"status": "retry", "max_retries": max_retries, "delay": delay}
        elif action == "continue":
            return {"status": "continue"}
        elif action == "stop":
            return {"status": "stop"}
        else:
            raise ValueError(f"Unknown response action: {action}")
    
    def _get_start_nodes(self, workflow_data: Dict) -> List[Dict]:
        """Get all nodes that have no incoming edges."""
        nodes = workflow_data["nodes"]
        edges = workflow_data["edges"]
        
        # Find nodes with no incoming edges
        node_ids_with_incoming = {edge["target"] for edge in edges}
        return [node for node in nodes if node["id"] not in node_ids_with_incoming]
    
    def _get_next_nodes(self, node_id: str, workflow_data: Dict) -> List[Dict]:
        """Get all nodes that come after the given node."""
        nodes = workflow_data["nodes"]
        edges = workflow_data["edges"]
        
        # Find outgoing edges
        outgoing_edges = [edge for edge in edges if edge["source"] == node_id]
        
        # Get target nodes
        return [
            node for node in nodes
            if any(edge["target"] == node["id"] for edge in outgoing_edges)
        ]
    
    def _get_error_handlers(self, node_id: str, workflow_data: Dict) -> List[Dict]:
        """Get error handler nodes connected to the given node."""
        next_nodes = self._get_next_nodes(node_id, workflow_data)
        return [
            node for node in next_nodes
            if node["type"] == NodeType.RESPONSE.value
            and node["data"]["responseType"] == "error"
        ]
    
    def _evaluate_response_conditions(self, response_data: Dict, result: Dict) -> bool:
        """Evaluate if a response node's conditions are met."""
        response_type = response_data["responseType"]
        
        if response_type == "success":
            return "error" not in result
        elif response_type == "error":
            return "error" in result
        elif response_type == "timeout":
            return result.get("status") == "timeout"
        
        return False
    
    def _replace_variables(self, data: Dict, variables: Dict) -> Dict:
        """Replace variables in the node data with their values."""
        data_str = json.dumps(data)
        
        # Replace variables in the format {{variable_name}}
        for var_name, var_value in variables.items():
            data_str = data_str.replace(f"{{{{{var_name}}}}}", str(var_value))
            
        return json.loads(data_str)
