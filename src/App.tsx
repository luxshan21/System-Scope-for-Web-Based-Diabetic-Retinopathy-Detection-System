import React, { useState } from 'react';
import { GoogleOAuthProvider, GoogleLogin, googleLogout } from '@react-oauth/google';
import axios from 'axios';
import './App.css';
import placeholderImage from './Login_image.png';

const CLIENT_ID = '382878482898-9lfn4jhrv03vafkjgabm12ul7o04tjg8.apps.googleusercontent.com';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [googleId, setGoogleId] = useState<string | null>(null);
  const [image, setImage] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [resultImageUrl, setResultImageUrl] = useState<string | null>(null);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSuccess = async (response: any) => {
    const idToken = response.credential;
    if (idToken) {
      const decodedToken = JSON.parse(atob(idToken.split('.')[1]));
      setUser(decodedToken);
      setIsAuthenticated(true);
      setGoogleId(decodedToken.sub);

      try {
        await axios.post('http://localhost:5000/login', {
          token: idToken,
          google_id: decodedToken.sub,
          name: decodedToken.name,
        });
      } catch (error) {
        console.error('Login failed:', error);
      }
    } else {
      console.error('No id_token found in the response:', response);
      setIsAuthenticated(false);
    }
  };

  const onFailure = () => {
    console.error('Login Failed');
    setIsAuthenticated(false);
  };

  const onLogoutSuccess = () => {
    googleLogout();
    setIsAuthenticated(false);
    setUser(null);
    setGoogleId(null);
    setImage(null);
    setAnalysisResult(null);
    setResultImageUrl(null);
    setProcessedImageUrl(null);
    setError(null);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      const fileType = selectedFile.type;
      const allowedTypes = ['image/jpeg', 'image/png'];

      if (!allowedTypes.includes(fileType)) {
        setError('Unsupported file type. Please upload a JPEG or PNG image.');
        setImage(null);
      } else {
        setImage(selectedFile);
        setError(null);
      }
    }
  };

  const handleImageUpload = async () => {
    if (!image) {
      setError('Please select an image to upload.');
      return;
    }

    if (!googleId) {
      setError('User ID not available. Please log in again.');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);
    formData.append('google_id', googleId!);
    formData.append('name', user.name);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        setAnalysisResult(response.data.analysisResult);
        setResultImageUrl(response.data.imageUrl);
        setProcessedImageUrl(response.data.processedImageUrl);
        setError(null);
      } else {
        console.error('Invalid response from the server:', response);
        setError('Invalid response from the server');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      setError('Network Error: Please try again later');
    }
  };

  return (
    <GoogleOAuthProvider clientId={CLIENT_ID}>
      <div className="App">
        <header className="App-header">
          <h1>Diabetic Retinopathy Detection System</h1>
          {!isAuthenticated ? (
            <div className="google-login-button">
              <GoogleLogin
                onSuccess={onSuccess}
                onError={onFailure}
                useOneTap
              />
            </div>
          ) : (
            <div className="container">
              <button onClick={onLogoutSuccess}>Logout</button>
              <div className="user-info">
                <h2>Welcome, {user?.name}</h2>
                {user?.picture ? (
                  <img src={user.picture} alt={user.name} />
                ) : (
                  <div className="placeholder-image">
                    <img src={placeholderImage} alt="placeholder" />
                  </div>
                )}
              </div>
              <div className="upload-section">
                <h2>Upload an Image for Analysis</h2>
                <label htmlFor="file-upload" className="custom-file-upload">
                  Choose Image
                </label>
                <input id="file-upload" type="file" accept="image/jpeg,image/png" onChange={handleImageChange} />
                <button onClick={handleImageUpload}>Upload Image</button>
                {error && <p className="error">{error}</p>}
              </div>
              <div className="result-section">
                {resultImageUrl && (
                  <div>
                    <h2>Uploaded Image:</h2>
                    <img src={resultImageUrl} alt="Uploaded Image" />
                  </div>
                )}
                {processedImageUrl && (
                  <div>
                    <h2>Processed Image:</h2>
                    <img src={processedImageUrl} alt="Processed Image" />
                  </div>
                )}
              </div>
            </div>
          )}
        </header>
      </div>
    </GoogleOAuthProvider>
  );
};

export default App;
