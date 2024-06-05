# System Scope for Web-Based Diabetic Retinopathy Detection System

## Overview

The objective of System Scope is to develop a user-friendly web-based platform that allows users to upload retinal images and receive detailed analysis regarding diabetic retinopathy. By integrating a pre-trained machine learning model, users can trust the system to accurately classify images into various stages of retinopathy. With Google Sign-In authentication, security is ensured, and users can easily manage their profiles and access historical data.

## Features and Functionalities

### User Authentication

- **Google Sign-In:** Enjoy secure access to the system with Google OAuth integration.
- **User Profile Management:** Easily manage user profiles, including login credentials and usage history.

### Image Upload

- **Upload Interface:** Intuitive interface for users to upload retinal images.
- **Supported Formats:** System supports common image formats (JPEG, PNG).

### Machine Learning Engine

- **Model Integration:** Pre-trained machine learning model (trained on Kaggle dataset) for image analysis.
- **Prediction:** Classify diabetic retinopathy into 5 classes: 'No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR'.

### Image Analysis and Results

- **Processing:** System processes uploaded images using the ML model.
- **Result Display:** Analysis results displayed to users, indicating the severity of diabetic retinopathy.

### Data Storage

- **User Data:** Maintain database of user data, including uploaded images and analysis history.

### User Interface

- **Dashboard:** User-friendly dashboard for managing uploads, viewing results, and accessing historical data.

## System Architecture

### Frontend

- **Technologies:** Built using React.js for responsive and interactive UI.
- **Google Sign-In Integration:** Utilizes Google OAuth API for authentication.

### Backend

- **Technologies:** Node.js/Express.js for server-side logic and API requests.
- **Machine Learning Integration:** Python with Flask for serving ML model and image processing.

### Database

- **Storage:** Relational database (e.g., MySQL) for storing user data and analysis results.

### Machine Learning

- **Model Training:** PyTorch pretrained model from Kaggle dataset for diabetic retinopathy detection.

## Screenshots

### Frontend View (Google Sign-In)
![image](https://github.com/luxshan21/System-Scope-for-Web-Based-Diabetic-Retinopathy-Detection-System/assets/81348451/8a7333ac-95f2-499c-8e53-2ade56da016e)



### Image Upload
![image](https://github.com/luxshan21/System-Scope-for-Web-Based-Diabetic-Retinopathy-Detection-System/assets/81348451/6d44db4d-955a-410f-82f5-e538cd58deae)


### Database View
![image](https://github.com/luxshan21/System-Scope-for-Web-Based-Diabetic-Retinopathy-Detection-System/assets/81348451/d747584e-0a39-4c8e-aace-6f022e904652)


