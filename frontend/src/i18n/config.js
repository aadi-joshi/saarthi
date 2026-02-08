import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// English translations
const en = {
  translation: {
    // Common
    app_name: 'SUVIDHA',
    app_subtitle: 'Smart Urban Digital Helpdesk',
    welcome: 'Welcome',
    continue: 'Continue',
    back: 'Back',
    cancel: 'Cancel',
    submit: 'Submit',
    confirm: 'Confirm',
    close: 'Close',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    retry: 'Retry',
    print: 'Print',
    download: 'Download',
    home: 'Home',
    
    // Services
    services: 'Services',
    electricity: 'Electricity',
    gas: 'Gas',
    water: 'Water',
    municipal: 'Municipal Services',
    
    // Actions
    pay_bill: 'Pay Bill',
    view_bills: 'View Bills',
    new_connection: 'New Connection',
    file_complaint: 'File Complaint',
    track_status: 'Track Status',
    upload_documents: 'Upload Documents',
    
    // Authentication
    login: 'Login',
    logout: 'Logout',
    enter_mobile: 'Enter Mobile Number',
    enter_otp: 'Enter OTP',
    send_otp: 'Send OTP',
    verify_otp: 'Verify OTP',
    resend_otp: 'Resend OTP',
    otp_sent: 'OTP sent to your mobile',
    invalid_otp: 'Invalid OTP. Please try again.',
    
    // Bill Payment
    bill_payment: 'Bill Payment',
    bill_number: 'Bill Number',
    bill_amount: 'Bill Amount',
    due_date: 'Due Date',
    pay_now: 'Pay Now',
    payment_method: 'Payment Method',
    payment_success: 'Payment Successful',
    payment_failed: 'Payment Failed',
    receipt_number: 'Receipt Number',
    transaction_id: 'Transaction ID',
    
    // Grievance
    grievance: 'Grievance',
    complaint: 'Complaint',
    category: 'Category',
    subject: 'Subject',
    description: 'Description',
    location: 'Location',
    tracking_id: 'Tracking ID',
    complaint_registered: 'Complaint Registered',
    
    // Connection
    connection_request: 'Connection Request',
    connection_type: 'Connection Type',
    applicant_name: 'Applicant Name',
    property_address: 'Property Address',
    application_fee: 'Application Fee',
    
    // Status
    status: 'Status',
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    rejected: 'Rejected',
    
    // Accessibility
    accessibility: 'Accessibility',
    high_contrast: 'High Contrast',
    elderly_mode: 'Elderly Mode',
    increase_text: 'Increase Text Size',
    decrease_text: 'Decrease Text Size',
    
    // Session
    session_timeout: 'Session Timeout',
    session_warning: 'Your session will expire in',
    seconds: 'seconds',
    extend_session: 'Extend Session',
    
    // Offline
    offline: 'Offline',
    offline_message: 'You are currently offline',
    transaction_queued: 'Transaction queued for sync',
    
    // Footer
    help: 'Help',
    contact: 'Contact',
    terms: 'Terms of Service',
    privacy: 'Privacy Policy',
    
    // Errors
    required_field: 'This field is required',
    invalid_mobile: 'Please enter a valid 10-digit mobile number',
    network_error: 'Network error. Please try again.',
    
    // Notifications
    notifications: 'Notifications',
    no_notifications: 'No active notifications',
  }
};

// Hindi translations
const hi = {
  translation: {
    // Common
    app_name: 'सुविधा',
    app_subtitle: 'स्मार्ट शहरी डिजिटल हेल्पडेस्क',
    welcome: 'स्वागत है',
    continue: 'जारी रखें',
    back: 'वापस',
    cancel: 'रद्द करें',
    submit: 'जमा करें',
    confirm: 'पुष्टि करें',
    close: 'बंद करें',
    loading: 'लोड हो रहा है...',
    success: 'सफल',
    error: 'त्रुटि',
    retry: 'पुनः प्रयास करें',
    print: 'प्रिंट',
    download: 'डाउनलोड',
    home: 'होम',
    
    // Services
    services: 'सेवाएं',
    electricity: 'बिजली',
    gas: 'गैस',
    water: 'पानी',
    municipal: 'नगरपालिका सेवाएं',
    
    // Actions
    pay_bill: 'बिल भुगतान',
    view_bills: 'बिल देखें',
    new_connection: 'नया कनेक्शन',
    file_complaint: 'शिकायत दर्ज करें',
    track_status: 'स्थिति ट्रैक करें',
    upload_documents: 'दस्तावेज़ अपलोड करें',
    
    // Authentication
    login: 'लॉगिन',
    logout: 'लॉगआउट',
    enter_mobile: 'मोबाइल नंबर दर्ज करें',
    enter_otp: 'OTP दर्ज करें',
    send_otp: 'OTP भेजें',
    verify_otp: 'OTP सत्यापित करें',
    resend_otp: 'OTP पुनः भेजें',
    otp_sent: 'आपके मोबाइल पर OTP भेजा गया',
    invalid_otp: 'अमान्य OTP। कृपया पुनः प्रयास करें।',
    
    // Bill Payment
    bill_payment: 'बिल भुगतान',
    bill_number: 'बिल नंबर',
    bill_amount: 'बिल राशि',
    due_date: 'देय तिथि',
    pay_now: 'अभी भुगतान करें',
    payment_method: 'भुगतान विधि',
    payment_success: 'भुगतान सफल',
    payment_failed: 'भुगतान विफल',
    receipt_number: 'रसीद नंबर',
    transaction_id: 'लेनदेन आईडी',
    
    // Grievance
    grievance: 'शिकायत',
    complaint: 'शिकायत',
    category: 'श्रेणी',
    subject: 'विषय',
    description: 'विवरण',
    location: 'स्थान',
    tracking_id: 'ट्रैकिंग आईडी',
    complaint_registered: 'शिकायत दर्ज',
    
    // Connection
    connection_request: 'कनेक्शन अनुरोध',
    connection_type: 'कनेक्शन प्रकार',
    applicant_name: 'आवेदक का नाम',
    property_address: 'संपत्ति का पता',
    application_fee: 'आवेदन शुल्क',
    
    // Status
    status: 'स्थिति',
    pending: 'लंबित',
    in_progress: 'प्रगति में',
    completed: 'पूर्ण',
    rejected: 'अस्वीकृत',
    
    // Accessibility
    accessibility: 'पहुंच',
    high_contrast: 'उच्च कंट्रास्ट',
    elderly_mode: 'वरिष्ठ नागरिक मोड',
    increase_text: 'टेक्स्ट बड़ा करें',
    decrease_text: 'टेक्स्ट छोटा करें',
    
    // Session
    session_timeout: 'सत्र समाप्त',
    session_warning: 'आपका सत्र समाप्त होने वाला है',
    seconds: 'सेकंड',
    extend_session: 'सत्र बढ़ाएं',
    
    // Offline
    offline: 'ऑफ़लाइन',
    offline_message: 'आप वर्तमान में ऑफ़लाइन हैं',
    transaction_queued: 'लेनदेन सिंक के लिए कतार में',
    
    // Footer
    help: 'सहायता',
    contact: 'संपर्क',
    terms: 'सेवा की शर्तें',
    privacy: 'गोपनीयता नीति',
    
    // Errors
    required_field: 'यह फ़ील्ड आवश्यक है',
    invalid_mobile: 'कृपया एक वैध 10-अंकीय मोबाइल नंबर दर्ज करें',
    network_error: 'नेटवर्क त्रुटि। कृपया पुनः प्रयास करें।',
    
    // Notifications
    notifications: 'सूचनाएं',
    no_notifications: 'कोई सक्रिय सूचना नहीं',
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en,
      hi,
    },
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
