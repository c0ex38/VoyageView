import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const EmailVerification = () => {
    const [verificationCode, setVerificationCode] = useState('');
    const [message, setMessage] = useState('');
    const location = useLocation();
    const navigate = useNavigate();
    const { userId, email } = location.state || {};

    const handleVerification = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/verify-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId, verification_code: verificationCode }),
            });

            const data = await response.json();

            if (response.ok) {
                navigate('/login');
            } else {
                setMessage(data.error || 'Verification failed.');
            }
        } catch (error) {
            setMessage('An error occurred. Please try again.');
        }
    };

    const handleResendCode = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/resend-verification-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage('Verification code resent successfully.');
            } else {
                setMessage(data.error || 'Failed to resend verification code.');
            }
        } catch (error) {
            setMessage('An error occurred. Please try again.');
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.heading}>Verify Your Email</h1>
                <p>We sent a verification code to {email}. Please enter it below.</p>
                <input
                    type="text"
                    placeholder="Enter verification code"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    style={styles.input}
                />
                <button onClick={handleVerification} style={styles.button}>
                    Verify Email
                </button>
                <button onClick={handleResendCode} style={styles.secondaryButton}>
                    Resend Code
                </button>
                {message && <p style={styles.message}>{message}</p>}
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f0f0f0',
    },
    card: {
        padding: '20px',
        borderRadius: '8px',
        backgroundColor: '#fff',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        maxWidth: '400px',
        width: '100%',
        textAlign: 'center',
    },
    heading: {
        marginBottom: '20px',
        fontSize: '24px',
        fontWeight: 'bold',
    },
    input: {
        padding: '10px',
        fontSize: '16px',
        border: '1px solid #ccc',
        borderRadius: '4px',
        marginBottom: '10px',
        width: '100%',
    },
    button: {
        padding: '10px',
        fontSize: '16px',
        color: '#fff',
        backgroundColor: '#007bff',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        marginBottom: '10px',
    },
    secondaryButton: {
        padding: '10px',
        fontSize: '16px',
        color: '#007bff',
        backgroundColor: '#f0f0f0',
        border: '1px solid #007bff',
        borderRadius: '4px',
        cursor: 'pointer',
    },
    message: {
        marginTop: '10px',
        color: 'green',
    },
};

export default EmailVerification;
