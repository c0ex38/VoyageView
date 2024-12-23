import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
    });

    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://127.0.0.1:8000/api/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();
            if (response.ok) {
                setMessage('Registration successful! Please verify your email.');
                setFormData({ username: '', email: '', password: '' });
                navigate('/verify-email', { state: { username: formData.username } }); // Kullanıcı doğrulama sayfasına yönlendirme
            } else {
                if (data.error === 'Username already exists.') {
                    setMessage('Username already exists. Checking status...');
                    checkUserStatus(formData.username); // Kullanıcı durumunu kontrol et
                } else {
                    setMessage(data.error || 'Registration failed.');
                }
            }
        } catch (error) {
            setMessage('An error occurred. Please try again.');
        }
    };

    const checkUserStatus = async (username) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/check-user-status/?username=${username}`, {
                method: 'GET',
            });
            const data = await response.json();

            if (response.ok) {
                if (data.status === 'unverified') {
                    navigate('/verify-email', { state: { username } }); // Doğrulama sayfasına yönlendirme
                } else if (data.status === 'verified') {
                    navigate('/login'); // Giriş sayfasına yönlendirme
                }
            } else {
                setMessage(data.error || 'An error occurred while checking user status.');
            }
        } catch (error) {
            setMessage('An error occurred while checking user status.');
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.heading}>Create an Account</h1>
                <form onSubmit={handleSubmit} style={styles.form}>
                    <input
                        type="text"
                        name="username"
                        placeholder="Enter your username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />
                    <input
                        type="email"
                        name="email"
                        placeholder="Enter your email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Enter your password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />
                    <button type="submit" style={styles.button}>
                        Register
                    </button>
                </form>
                {message && (
                    <p
                        style={{
                            ...styles.message,
                            color: message.includes('successful') ? 'green' : 'red',
                        }}
                    >
                        {message}
                    </p>
                )}
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
        backgroundColor: '#f9f9f9',
    },
    card: {
        backgroundColor: '#fff',
        padding: '30px',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        maxWidth: '400px',
        width: '100%',
        textAlign: 'center',
    },
    heading: {
        marginBottom: '20px',
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '15px',
    },
    input: {
        padding: '10px',
        fontSize: '16px',
        borderRadius: '4px',
        border: '1px solid #ddd',
        width: '100%',
        boxSizing: 'border-box',
    },
    button: {
        padding: '10px',
        fontSize: '16px',
        borderRadius: '4px',
        backgroundColor: '#007bff',
        color: '#fff',
        border: 'none',
        cursor: 'pointer',
        transition: 'background-color 0.3s ease',
    },
    message: {
        marginTop: '20px',
        fontSize: '14px',
    },
};

export default Register;
