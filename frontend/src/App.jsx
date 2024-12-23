import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import EmailVerification from "./pages/EmailVerification";
import Login from "./pages/Login";
import Profile from "./pages/Profile";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Register />} />
                <Route path="/register" element={<Register />} />
                <Route path="/verify-email" element={<EmailVerification />} />
                <Route path="/login" element={<Login />} />
                <Route path="/profile" element={<Profile />} />
            </Routes>
        </Router>
    );
};

export default App;
