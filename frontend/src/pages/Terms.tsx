import React from 'react';

export default function Terms() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Terms of Service</h1>
      
      <div className="space-y-6">
        <section>
          <h2 className="text-xl font-semibold mb-3">1. Agreement</h2>
          <p className="text-gray-700">
            By accessing or using the Dyligent messaging automation platform ("Service"), you agree to be bound by these Terms of Service ("Terms"). 
            If you disagree with any part of the terms, you may not access the Service.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">2. Use License</h2>
          <p className="text-gray-700">
            Dyligent grants you a limited, non-exclusive, non-transferable, revocable license to use the Service strictly in accordance 
            with these Terms and any additional terms provided to you.
          </p>
          <p className="text-gray-700 mt-2">
            You agree not to:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>Modify or copy the materials outside of normal Service usage</li>
            <li>Use the materials for any commercial purpose not authorized by Dyligent</li>
            <li>Attempt to decompile or reverse engineer any software contained in the Service</li>
            <li>Remove any copyright or other proprietary notations from the materials</li>
            <li>Transfer the materials to another person or entity</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">3. Messaging and Communications</h2>
          <p className="text-gray-700">
            The Service allows for the sending of automated messages to end users. You agree:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>To comply with all applicable laws and regulations regarding SMS/MMS messaging</li>
            <li>To obtain proper consent from recipients before sending messages</li>
            <li>Not to send spam, unsolicited messages, or content that violates any laws</li>
            <li>To honor opt-out requests promptly and maintain proper records</li>
            <li>That you are solely responsible for the content of all messages sent through the Service</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">4. User Accounts</h2>
          <p className="text-gray-700">
            When you create an account with us, you must provide accurate and complete information. You are responsible for 
            maintaining the security of your account and password. Dyligent cannot and will not be liable for any loss or damage 
            resulting from your failure to comply with this security obligation.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">5. Limitation of Liability</h2>
          <p className="text-gray-700">
            In no event shall Dyligent be liable for any damages (including, without limitation, damages for loss of data or profit, 
            or due to business interruption) arising out of the use or inability to use the Service, even if Dyligent or a Dyligent 
            authorized representative has been notified orally or in writing of the possibility of such damage.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">6. Indemnification</h2>
          <p className="text-gray-700">
            You agree to indemnify and hold harmless Dyligent, its affiliates, officers, directors, employees, and agents from and 
            against any and all claims, liabilities, damages, losses, costs, expenses, or fees arising from your use of the Service 
            or violation of these Terms.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">7. Termination</h2>
          <p className="text-gray-700">
            We may terminate or suspend access to our Service immediately, without prior notice or liability, for any reason whatsoever, 
            including without limitation if you breach the Terms. All provisions of the Terms which by their nature should survive 
            termination shall survive termination.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">8. Governing Law</h2>
          <p className="text-gray-700">
            These Terms shall be governed and construed in accordance with the laws of the United States, 
            without regard to its conflict of law provisions.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">9. Changes</h2>
          <p className="text-gray-700">
            We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material 
            we will try to provide at least 30 days' notice prior to any new terms taking effect. What constitutes a material change 
            will be determined at our sole discretion.
          </p>
          <p className="text-gray-700 mt-2">
            This policy was last updated on {new Date().toLocaleDateString()}.
          </p>
        </section>
      </div>
    </div>
  );
}
