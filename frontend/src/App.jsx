import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AccessibilityProvider } from './context/AccessibilityContext';
import { SessionProvider } from './context/SessionContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Bills from './pages/Bills';
import BillPayment from './pages/BillPayment';
import Grievance from './pages/Grievance';
import GrievanceTrack from './pages/GrievanceTrack';
import Connection from './pages/Connection';
import Track from './pages/Track';
import Receipt from './pages/Receipt';

function App() {
    return (
        <AuthProvider>
            <AccessibilityProvider>
                <SessionProvider>
                    <Routes>
                        <Route element={<Layout />}>
                            <Route path="/" element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/bills" element={<Bills />} />
                            <Route path="/bills/pay/:id" element={<BillPayment />} />
                            <Route path="/grievance" element={<Grievance />} />
                            <Route path="/grievance/track" element={<GrievanceTrack />} />
                            <Route path="/connection" element={<Connection />} />
                            <Route path="/track" element={<Track />} />
                            <Route path="/receipt/:type/:id" element={<Receipt />} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Route>
                    </Routes>
                </SessionProvider>
            </AccessibilityProvider>
        </AuthProvider>
    );
}

export default App;
