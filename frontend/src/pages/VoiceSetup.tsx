import { VoiceWizard } from '../components/wizard/VoiceWizard';
import { WizardProvider } from '../contexts/WizardContext';

export default function VoiceSetup() {
  return (
    <WizardProvider>
      <VoiceWizard />
    </WizardProvider>
  );
}
