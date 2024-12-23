import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Profile = () => {
    const [profileData, setProfileData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProfile = async () => {
            const accessToken = localStorage.getItem("access_token"); // Token localStorage'dan alınır

            if (!accessToken) {
                navigate("/login"); // Eğer token yoksa login sayfasına yönlendir
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:8000/api/profile/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`, // Token başlığa eklenir
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setProfileData(data);
                } else if (response.status === 401) {
                    // Token geçersizse login sayfasına yönlendir
                    localStorage.removeItem("access_token");
                    navigate("/login");
                } else {
                    setError("Failed to fetch profile data.");
                }
            } catch (err) {
                setError("An error occurred while fetching profile data.");
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [navigate]);

    if (loading) {
        return <div style={styles.loading}>Loading...</div>;
    }

    if (error) {
        return <div style={styles.error}>{error}</div>;
    }

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <div style={styles.header}>
                    <img
                        src={profileData.profile_image || "https://via.placeholder.com/100"}
                        alt="Profile"
                        style={styles.profileImage}
                    />
                    <h2 style={styles.username}>{profileData.level_message}</h2>
                    <p style={styles.bio}>{profileData.bio || "No bio available"}</p>
                </div>
                <div style={styles.details}>
                    <div style={styles.detailItem}>
                        <strong>Location:</strong>
                        <span>{profileData.location || "Not specified"}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Phone:</strong>
                        <span>{profileData.phone_number || "Not specified"}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Gender:</strong>
                        <span>{profileData.gender || "Not specified"}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Birth Date:</strong>
                        <span>{profileData.birth_date || "Not specified"}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Level:</strong>
                        <span>{`Level ${profileData.level} - ${profileData.points} Points`}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Followers:</strong>
                        <span>{profileData.followers_count}</span>
                    </div>
                    <div style={styles.detailItem}>
                        <strong>Following:</strong>
                        <span>{profileData.following_count}</span>
                    </div>
                </div>
                <div style={styles.badge}>
                    <img src={profileData.level_badge.icon} alt="Badge" style={styles.badgeImage} />
                    <p>{profileData.level_badge.message}</p>
                </div>
                <button style={styles.editButton}>Edit Profile</button>
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
        backgroundColor: "#f4f4f9",
    },
    card: {
        backgroundColor: "#fff",
        borderRadius: "10px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        padding: "20px",
        maxWidth: "500px",
        width: "100%",
        textAlign: "center",
    },
    header: {
        marginBottom: "20px",
    },
    profileImage: {
        width: "100px",
        height: "100px",
        borderRadius: "50%",
        objectFit: "cover",
        marginBottom: "10px",
    },
    username: {
        fontSize: "20px",
        fontWeight: "bold",
        margin: "10px 0",
    },
    bio: {
        fontSize: "14px",
        color: "#555",
        marginBottom: "20px",
    },
    details: {
        textAlign: "left",
        marginBottom: "20px",
    },
    detailItem: {
        display: "flex",
        justifyContent: "space-between",
        marginBottom: "10px",
        fontSize: "14px",
        color: "#333",
    },
    badge: {
        marginTop: "20px",
        textAlign: "center",
    },
    badgeImage: {
        width: "50px",
        height: "50px",
        marginBottom: "10px",
    },
    editButton: {
        padding: "10px 20px",
        fontSize: "14px",
        color: "#fff",
        backgroundColor: "#007bff",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
        transition: "background-color 0.3s ease",
    },
    editButtonHover: {
        backgroundColor: "#0056b3",
    },
    loading: {
        textAlign: "center",
        fontSize: "18px",
        color: "#333",
    },
    error: {
        textAlign: "center",
        fontSize: "16px",
        color: "red",
    },
};

export default Profile;
