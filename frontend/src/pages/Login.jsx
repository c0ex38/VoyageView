import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
    const [formData, setFormData] = useState({
        username: "",
        password: "",
    });

    const [message, setMessage] = useState("");
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch("http://127.0.0.1:8000/api/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const data = await response.json();
                // Tokenları localStorage'a kaydet
                localStorage.setItem("accessToken", data.access);
                localStorage.setItem("refreshToken", data.refresh);
                setMessage("Login successful!");
                navigate("/profile"); // Kullanıcıyı profile sayfasına yönlendir
            } else {
                const errorData = await response.json();
                setMessage(errorData.error || "Login failed.");
            }
        } catch (error) {
            setMessage("An error occurred. Please try again.");
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.heading}>Login</h1>
                <form onSubmit={handleSubmit} style={styles.form}>
                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />
                    <button type="submit" style={styles.button}>
                        Login
                    </button>
                </form>
                {message && (
                    <p
                        style={{
                            ...styles.message,
                            color: message.includes("successful") ? "green" : "red",
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
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f9f9f9",
    },
    card: {
        backgroundColor: "#fff",
        padding: "30px",
        borderRadius: "8px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        maxWidth: "400px",
        width: "100%",
        textAlign: "center",
    },
    heading: {
        marginBottom: "20px",
        fontSize: "24px",
        fontWeight: "bold",
        color: "#333",
    },
    form: {
        display: "flex",
        flexDirection: "column",
        gap: "15px",
    },
    input: {
        padding: "10px",
        fontSize: "16px",
        borderRadius: "4px",
        border: "1px solid #ddd",
        width: "100%",
        boxSizing: "border-box",
    },
    button: {
        padding: "10px",
        fontSize: "16px",
        borderRadius: "4px",
        backgroundColor: "#007bff",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        transition: "background-color 0.3s ease",
    },
    message: {
        marginTop: "20px",
        fontSize: "14px",
    },
};

export default Login;
