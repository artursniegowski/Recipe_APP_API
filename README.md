# Recipe_APP_API </br>
## AWS EC2 READY </br>

[![GitHub marketplace](https://img.shields.io/badge/marketplace-docker--login-blue?logo=github&style=flat-square)](https://github.com/marketplace/actions/docker-login) 
[![Test and Lint](https://github.com/artursniegowski/Recipe_APP_API/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/artursniegowski/Recipe_APP_API/actions/workflows/checks.yml)

</br>
The Recipe API is a fully functioning and robust web application built using Python, Django, and Django REST framework. The primary goal of this project is to provide users with a powerful and user-friendly API for managing their favorite recipes. Leveraging modern technologies and industry best practices, the Recipe API offers a seamless experience for creating, organizing, and sharing recipes.</br>

</br>

## Technologies Used: </br>
- Python: The core programming language used for backend development.</br>
- Django: A high-level web framework that provides a strong foundation for building web applications.</br>
- Django REST framework: An extension of Django that simplifies the creation of RESTful APIs.</br>
- PostgreSQL: A powerful and scalable open-source relational database management system for data storage.</br>
- Docker: Used for containerization, allowing easy deployment and scalability.</br>
- Docker Hub: A platform for finding and sharing container images, facilitating smooth deployment processes.</br>
- Swagger: Automated API documentation that makes it easy to explore and test API endpoints.</br>
- GitHub Actions: Used for continuous integration and continuous deployment (CI/CD) to automate testing and linting whenever code is pushed to GitHub.</br>
- Flake8: A tool for enforcing style guide rules and ensuring code quality.</br>
- TDD (Test Driven Development): The project was developed using TDD principles, where tests were written before implementing functionality.</br>

</br>


## Key Features of the Recipe API:</br>
1. Custom User Models: The API supports custom user models for user registration and authentication, ensuring a secure and personalized experience.</br>
2. Admin Overview: An intuitive admin interface allows for easy management and monitoring of the application.</br>
3. User API: Authenticated users can register, generate authentication tokens, and view/update their profiles.</br>
4. Recipe API: Authenticated users can create, list, view, update, and delete their recipes. The API also supports nested serializers for better data organization.</br>
5. Tags API: Tags can be listed, updated, and deleted, providing users with the ability to organize their recipes effectively.</br>
6. Unit Testing: Extensive unit testing has been implemented to ensure the reliability and stability of the application.</br>
7. The Recipe API's user-friendly interface and advanced functionalities cater to individuals passionate about food and cooking. With features like uploading images, filtering, and sorting recipes, users can efficiently manage their culinary creations and discover new ideas. The project's adherence to Test Driven Development ensures high code quality, reducing the chances of bugs and errors.</br>

</br>

**Whether you are a home cook, professional chef, or simply a food enthusiast, the Recipe API is the perfect tool to organize and explore the wonderful world of recipes, making cooking an even more enjoyable experience.**</br>


</br>


The Recipe API project is not only a powerful standalone application for managing recipes, but it also provides an ideal backend solution for anyone looking to develop a frontend application, such as a web or mobile app, using popular frontend frameworks like React.</br>

With its comprehensive set of API endpoints, user authentication, and efficient data management capabilities, the Recipe API serves as an excellent backend foundation for building feature-rich frontend interfaces. By integrating React or any other frontend technology, developers can create visually appealing and interactive interfaces that seamlessly interact with the Recipe API.</br>



## Here are some benefits of using the Recipe API as the backend for a frontend application:</br>
1. API Compatibility: The Recipe API follows RESTful design principles, making it compatible with various frontend frameworks and libraries. Developers can make HTTP requests to the API endpoints to fetch and manipulate data.</br>

2. Data Management: The Recipe API handles all the data management operations, including user profiles, recipes, and tags. Frontend developers can focus on designing user interfaces and let the backend handle data storage and retrieval.</br>

3. Authentication and Security: The custom user model and authentication system of the Recipe API ensure secure user registration and login processes. This helps in building frontend applications with robust user management features.</br>

4. Modularity: Separating the frontend and backend concerns allows for a more modular approach to application development. Developers can work independently on both components, making it easier to maintain and scale the application.</br>

5. Scalability: By having the Recipe API as the backend, developers can deploy and scale the frontend and backend components independently. This enables seamless expansion to accommodate increasing user traffic.</br>

6. Code Reusability: Using the Recipe API as the backend can save development time and effort. Many features, such as user authentication and recipe management, are already implemented in the backend, allowing developers to reuse and build upon these functionalities in the frontend.</br>



**In summary, the Recipe API not only serves as a full-fledged recipe management system but also offers a solid foundation for building frontend applications with frameworks like React. Its RESTful architecture, user-friendly API documentation, and integration capabilities make it a perfect choice for developers looking to create modern and feature-rich frontend applications backed by a reliable and efficient backend system.**</br>


---

## The Recipe API project is fully prepared for deployment to AWS EC2, providing a scalable and reliable cloud infrastructure for hosting the application and ensuring worldwide availability to users.</br>


---


The necessary steps to make the program work (local machine):</br>
1. Clone or Fork the project.</br>
2. Change the name of .env.template to .env.</br>
3. Define the environmental variables in .env :</br>
**POSTGRES_USERNAME**="devuser"</br>
**POSTGRES_PASSWORD**="changeme"</br>
**DB_NAME**=dbname</br>
**DJANGO_SECRET_KEY**='your_djanog_secret_key'</br>
**DJANGO_ALLOWED_HOSTS**=127.0.0.1</br>
4. You need to have installed docker https://docs.docker.com/get-docker/ , </br>
and then navigate to the main folder and run the command to build the docker image: </br>
**docker-compose build**  - to build the docker image with docker-compose.yml</br>
**docker-compose up** - to start the development server</br>
5. The API shoudl be available at http://127.0.0.1:8000/ or you can check the SWAGER docs under http://127.0.0.1:8000/api/docs/ where you can test it. </br>


---

GOOD to know:</br>
1. You can check the documentation offline - [View PDF](docs/Swagger-docs.pdf)</br>
The documentation includes all the endpoints and how to use them. Additionally you can also use: </br>
- http://127.0.0.1:8000/admin </br>
- http://127.0.0.1:8000/api/docs/ </br>
- http://127.0.0.1:8000/api/redoc/ </br>
2. If you inted to run the GitHub Actions for autonomous testing and linting the porject you will need to configure the Repository secrets in your Repository:</br>
**DOCKERHUB_USER**="your_user_name"</br>
**DOCKERHUB_TOKEN**="your_user_token"</br>
3. There is a separate  file for deploying to AWS on EC2, which should be used if you choose to deploy it on the cloud. You have to use the docker-compose-deploy.yml.</br>
4. Useful commands:</br>
**docker-compose run --rm app sh -c "python manage.py createsuperuser"** - creating super user via docker </br>
**docker-compose run --rm app sh -c "python manage.py test"** - run the unit tests via docker </br>
**docker-compose run --rm app sh -c "flake8"** - run the lining checker flake8 via docker </br>
**docker-compose down** - clear containers </br>
**docker-compose -f docker-compose-deploy.yml up** - starting services with the deployment docker compose file that should be used after deploying.  </br>

---

## Components used for deployment</br>

1. Nginx: Nginx is a powerful and popular web server that serves as the frontend or reverse proxy for the application. It efficiently handles incoming client requests and distributes them to the appropriate backend servers, like uWSGI. Nginx is known for its speed, scalability, and security, making it an excellent choice for production-grade deployments.</br>

2. uWSGI: uWSGI is a high-performance application server that interfaces with Nginx and serves as the WSGI server for the Django application. It efficiently processes incoming requests from Nginx, runs the Django application, and returns the responses back to Nginx. Like Gunicorn, uWSGI is simple to use and provides excellent performance for serving Django applications. </br>

3. Docker Compose: Docker Compose is a tool for defining and managing multi-container Docker applications. It allows you to define the services, networks, and volumes required for the deployment of your application in a single YAML file. Using Docker Compose, you can easily pull together the Nginx, uWSGI, and Django application services, ensuring they work seamlessly together and can be easily deployed on your server. </br>

</br>
</br>


A reverse proxy is a crucial component in deploying Django applications because it optimizes the handling of incoming client requests and ensures efficient handling of static content. While the WSGI server that runs Python, like uWSGI, is excellent at executing Python code for dynamic content, it may not perform optimally when serving static files like CSS, JS, and images. Scaling the application to handle a high volume of requests for static content can lead to suboptimal performance.</br>

To address this, we leverage the capabilities of a web server, which excels at efficiently serving static files. Web servers can handle a large number of requests for specific files, thanks to the resources allocated to the server. By setting up a reverse proxy using a web server application, we can efficiently serve static files through the proxy, while simultaneously forwarding other requests to the WSGI server to be handled by the Python code.</br>

This configuration ensures that the WSGI server focuses on processing dynamic content, where its strength lies, while offloading the static file serving to the web server via the reverse proxy. As a result, the reverse proxy optimizes the overall performance of the Django application, enabling it to handle many thousands or even millions of requests efficiently, making it a best practice for Django deployment in production environments.</br>


