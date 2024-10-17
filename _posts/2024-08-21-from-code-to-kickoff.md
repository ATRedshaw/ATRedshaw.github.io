---
# bundle exec jekyll s - Command to run locally
# bundle exec jekyll build - Command to build to github pages
title: "From Code to Kick-Off: Building a Premier League Prediction App with Flask, Firebase, and ReactJS"
date: 2024-08-05 09:00:00 BST
categories: [Web Development,  Full-Stack]
tags: [web, webdev, web development, fullstack, full-stack, full stack development, frontend, front-end, front end development, backend, back-end, back end development, python, flask, react, reactjs, javascript, ui, ux, user interface, user experience, tailwind, tailwindcss, css, styling, framer-motion, animation, transitions, firebase, firestore, nosql, database, authentication, api, rest, restful api, fpl, fantasy premier league, football, soccer, prediction, league, match, sports, app, web application, deployment, github actions, cron jobs, data processing, data transformation, proxy server, mobile-first, responsive design, real-time updates, private league, scalability, security]
math: true
---
The thrill of predicting football outcomes and competing with friends and family has always been a captivating pastime.  Five years ago, my family's engagement with a now-defunct prediction app sparked my interest in developing a modern, feature-rich platform to recapture that excitement.  This article details the journey of building the [**(Redshaw) Premier Predictor**](https://redshaw-premier-predictor.onrender.com/), a full-stack web application designed for Premier League enthusiasts, leveraging React, Flask, Firebase, and a touch of friendly competition.

### Project Genesis and Core Requirements

The project's genesis stemmed from a desire to replicate and enhance the functionality of the older, discontinued prediction app.  Beyond simply predicting match outcomes, the vision expanded to encompass pre-season league table predictions, fostering a more comprehensive engagement with the Premier League. This vision translated into the following core requirements:

1. **Mobile-First, Responsive Design:**  A clean, intuitive user interface adaptable to various screen sizes, ensuring a seamless experience across devices.

2. **Real-Time Updates:** Live updates on scores, standings, and user rankings to maintain engagement and provide immediate feedback.

3. **Private League Functionality:**  The ability to create and join private leagues, fostering competition amongst friends and family.

4. **Dual Prediction Modes:**  Supporting both pre-season league table predictions and weekly match predictions.

5. **Enforced Prediction Deadlines:**  Strict deadlines for submissions to ensure fair play and heighten anticipation.  Post-deadline visibility of league members' predictions for comparison and analysis.

6. **Secure Authentication:**  Robust email-verified user authentication to protect user data and maintain platform integrity.

### Technology Stack Rationale

The choice of technologies was driven by a combination of familiarity, performance considerations, and the specific requirements of the project.

**Frontend (React with Tailwind CSS and Framer Motion):**  My prior experience with React, coupled with the desire for a highly customisable and visually appealing interface, led to this choice. Tailwind CSS provided the flexibility for rapid UI development and responsive design, while Framer Motion facilitated smooth animations and transitions, enhancing user experience.  This offered a more tailored design approach compared to pre-built component libraries.

**Backend (Flask, Firebase, and FPL API):**  Firebase provides a robust backend-as-a-service (BaaS) solution for user authentication and initial data storage using Firestore, its NoSQL database.  Flask, a lightweight Python web framework, serves as an API gateway and proxy for the Fantasy Premier League (FPL) API, allowing for data transformation and custom endpoint creation tailored to the app's specific needs.  This architecture allows for efficient handling of data from the FPL API and provides the flexibility to create custom logic for scoring and league management. The decision to use Python for the Flask server stemmed from familiarity and ease of deployment, resolving earlier challenges faced with a Node.js Express server.

To mitigate excessive reads against Firestore, particularly for viewing performance statistics (both individual and within leagues), point totals and rankings are pre-calculated and cached. This optimisation is crucial for scalability and staying within Firestore's read/write limits.  These calculations are performed by scheduled cron jobs using GitHub Actions, ensuring data is updated regularly without requiring constant on-demand calculations. This approach significantly reduces the load on Firestore and improves the overall performance and responsiveness of the application.

![image](/assets/img/code-to-kickoff/architecture-diagram.png)
_Figure 1: The architecture for the full project._

### Frontend Architecture: Public and Protected Routes

The frontend architecture employs a clear separation between public and protected routes using React Router, managing access based on user authentication status.

![image](/assets/img/code-to-kickoff/frontend-routes.png)
_Figure 2: Frontend routes for the full project._

**Public Routes:** These routes, including the landing page, scoring guide, signup, and login pages, are accessible to all users, providing essential information and encouraging engagement.

**Protected Routes:**  Accessible only to authenticated users, these routes encompass the core application functionality: submitting predictions, viewing performance statistics, managing leagues, accessing leaderboards, and configuring account settings.  Protection is implemented by checking for an authentication token and redirecting unauthorised users to the login page.

Data retrieval within React components is handled using `Axios`, a promise-based HTTP client, simplifying asynchronous operations and data handling compared to the native `fetch` API.

### Backend Implementation: Flask, Firebase, and API Integration

The backend leverages Flask as an API gateway and proxy for the FPL API, while Firebase handles user authentication and data persistence.

**Flask as API Proxy:**  Flask facilitates data transformation and formatting, optimising data transfer to the frontend.  It also enables the creation of custom endpoints tailored to the application's needs, such as the `/api/table-predictions/live-table` endpoint, which aggregates and formats data from the FPL API to provide a live league table with integrated scoring logic. All Flask endpoints are publicly accessible, with Firebase handling authentication and authorisation separately.

**Firebase Integration:** Firebase provides secure user authentication, including email/password login, verification, and password reset.  Firestore, Firebase’s NoSQL database, offers flexible and scalable data storage. Firebase Security Rules ensure data integrity and restrict access based on user roles and permissions.

Communication between the React frontend and Flask backend adheres to RESTful API principles, using JSON for efficient data exchange.


### Reflections and Future Directions

Developing the Premier Predictor has been a significant learning experience, reinforcing my understanding of full-stack development and the nuances of integrating various technologies.  The initial challenges with Tailwind CSS's customisability ultimately resulted in a more polished and visually appealing application.  Transitioning from a Node.js Express server to Python/Flask streamlined the deployment process and leveraged my existing Python expertise.

Future development will focus on enhancing application scalability, providing greater user customisation options, and migrating from the BaaS Firebase model to a full Flask backend managing accounts, authentication, and data storage. This will provide greater control over the system and facilitate the implementation of more advanced features, such as:

* **Enhanced Statistical Analysis:** Providing users with detailed performance metrics and predictive analytics.
* **Head-to-Head Matchups:** Implementing features for direct competition between users within leagues.
* **Live Match Tracking and Notifications:**  Pushing real-time updates and notifications to users during live matches.
* **Integration with Social Media Platforms:** Enabling users to share their predictions and league standings.


This project represents a continuous evolution, driven by the desire to create a truly engaging and comprehensive platform for Premier League prediction enthusiasts.  The journey from code to kick-off has been both challenging and rewarding, and the future holds exciting possibilities for further innovation and enhancement.
