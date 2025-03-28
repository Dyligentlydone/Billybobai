import express from 'express';
import twilio from 'twilio';
import { Request, Response } from 'express';

const router = express.Router();

router.post('/preview', async (req: Request, res: Response) => {
  try {
    const { text, voice, speed = 1, pitch = 1, emphasis = 'normal', accountSid, authToken } = req.body;

    if (!text || !voice || !accountSid || !authToken) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }

    // Initialize Twilio client with provided credentials
    const client = twilio(accountSid, authToken);

    // Create TwiML with voice settings
    const twiml = new twilio.twiml.VoiceResponse();
    
    // Wrap the text in SSML prosody tags
    const ssmlText = `
      <speak>
        <prosody rate="${speed * 100}%" pitch="${pitch * 100}%">
          ${text}
        </prosody>
      </speak>
    `.trim();

    twiml.say({ voice }, ssmlText);

    // Convert TwiML to audio using Twilio's Media API with timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    try {
      const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Calls/TTS.mp3`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`${accountSid}:${authToken}`).toString('base64')}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          Twiml: twiml.toString()
        }).toString(),
        signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.message || 
          `Twilio API error: ${response.status} ${response.statusText}`
        );
      }

      const audioBuffer = await response.arrayBuffer();

      // Send the audio back to the client
      res.set({
        'Content-Type': 'audio/mpeg',
        'Content-Length': audioBuffer.byteLength,
        'Cache-Control': 'no-cache'
      });
      res.send(Buffer.from(audioBuffer));

    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    }

  } catch (error) {
    console.error('TTS Preview Error:', error);
    
    if (error.message === 'Request timed out') {
      return res.status(504).json({
        error: 'Gateway timeout',
        details: 'The request took too long to process'
      });
    }

    res.status(500).json({ 
      error: 'Failed to generate voice preview',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
