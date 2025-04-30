import React from 'react';
import { Link } from 'react-router-dom';

export default function Privacy() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Privacy Policy</h1>
      
      <div className="space-y-6">
        <section>
          <h2 className="text-xl font-semibold mb-3">Introduction</h2>
          <p className="text-gray-700">
            Dyligent ("we", "our", or "us") respects your privacy and is committed to protecting your personal data. 
            This privacy policy will inform you about how we look after your personal data when you visit our website 
            and tell you about your privacy rights and how the law protects you.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">Data Collected</h2>
          <p className="text-gray-700">
            We may collect, use, store and transfer different kinds of personal data about you which we have grouped together as follows:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>Identity Data: includes first name, last name, username or similar identifier.</li>
            <li>Contact Data: includes email address and telephone numbers.</li>
            <li>Technical Data: includes internet protocol (IP) address, browser type and version, time zone setting and location, browser plug-in types and versions, operating system and platform, and other technology on the devices you use to access this website.</li>
            <li>Usage Data: includes information about how you use our website, products, and services.</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">How We Use the Data</h2>
          <p className="text-gray-700">
            We will only use your personal data when the law allows us to. Most commonly, we will use your personal data in the following circumstances:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>To provide our services to you</li>
            <li>To respond to your inquiries</li>
            <li>To improve our website and services</li>
            <li>To comply with legal obligations</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">SMS & Messaging Communications</h2>
          <p className="text-gray-700">
            When you register for our services, you may receive SMS messages as part of the service. Message frequency varies. 
            Message and data rates may apply. You can opt out of receiving SMS messages at any time by replying "STOP" to any message received from us.
          </p>
          
          <div className="mt-3 p-4 border-l-4 border-gray-300 bg-gray-50">
            <p className="text-gray-700 font-medium">
              "We do not share, sell, or rent mobile contact information with third parties or affiliates for marketing or promotional purposes."
            </p>
          </div>
          
          <h3 className="text-lg font-medium mt-4 mb-2">Opt-In Mechanism</h3>
          <p className="text-gray-700">
            Our website's opt-in process for SMS communications includes:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>A checkbox (not pre-selected) for users to consent to receive SMS messages</li>
            <li>A clear statement of consent:</li>
          </ul>
          
          <div className="mt-2 p-4 border-l-4 border-gray-300 bg-gray-50">
            <p className="text-gray-700 font-medium">
              "By providing your phone number, you agree to receive text messages from Dyligent. Message and data rates may apply. Message frequency varies. Reply STOP to unsubscribe."
            </p>
          </div>
          
          <p className="text-gray-700 mt-3">
            This opt-in process aligns with best practices for web form opt-ins and regulatory requirements.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">Data Security</h2>
          <p className="text-gray-700">
            We have put in place appropriate security measures to prevent your personal data from being accidentally lost, used, or 
            accessed in an unauthorized way, altered, or disclosed. We limit access to your personal data to those employees, agents, 
            contractors, and other third parties who have a business need to know.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">Legal Rights</h2>
          <p className="text-gray-700">
            Under certain circumstances, you have rights under data protection laws in relation to your personal data, including the right to:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-700">
            <li>Request access to your personal data</li>
            <li>Request correction of your personal data</li>
            <li>Request erasure of your personal data</li>
            <li>Object to processing of your personal data</li>
            <li>Request restriction of processing your personal data</li>
            <li>Request transfer of your personal data</li>
            <li>Right to withdraw consent</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-3">Changes to This Policy</h2>
          <p className="text-gray-700">
            We may update this privacy policy from time to time. We will notify you of any changes by posting the new privacy policy on this page.
            This policy was last updated on {new Date().toLocaleDateString()}.
          </p>
        </section>
        
        {/* Contact Us Button */}
        <section className="mt-8 text-center">
          <Link to="/contact" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Contact Us
          </Link>
        </section>
      </div>
    </div>
  );
}
