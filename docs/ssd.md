# SYSTEM SPECIFICATION DOCUMENT

## 1. Introduction

### 1.1 Purpose of the document
The following document is meant to describe the requirements, in their most general definition, for "Recipe Suggester Tool", realized as a final project for the course 440MI Machine Learning Operations at University of Trieste.
The document will follow the standard structure specified in IEEE/ANSI 830-1998. 

### 1.2 Scope of the product
The product "Recipe Suggester Tool" will provide real-time, step-by-step and easy-to-cook recipes to the user, based on the food recognized in pictures provided by the user himself.

### 1.3 Definitions, acronyms and abbreviations
RST: Rec Suggester Tool, the name of the product
[TODO]

---

## 2. General description

### 2.1 Product perspective
The system architecture follows a Client-Server method. The user interact with the product via a web-app hosted online. 
The web-app is connected to a backend through a Fast API .

### 2.2 Product function
The user send to the frontend a picture of food - e.g. sending a picture of a fridge. \
The webapp sends the picture to the Backend. \
The backend loads a machine learning trained module and sends the picture to it. \
The ML module will be able to recognize specific types of food into the picture. \
The types of food recognized are then sent to an OpenAI LLM via API. \
The LLM will organize and builds a recipe based on the food recieved. \
The recipe text will then be sent to the webapp in order to be shown to the user.

### 2.3 User characteristics
A user is a common person in need of advice for deciding what -  and how - to cook.
The user should be register in order to use the product.
The user should use his/her own OpenAI API key in order to use the product (TBD!).

### 2.4 General constraints
The whole workflow will require at most 10 seconds.
The product should be robust to manage multiple (at least 5) concurrent multiple accesses.
The product should be robust to failures, i.e. the API not working.
The percentage of events causing failures should be below 1%.
The percentage of data corruption on failure should be below 1%.
The product should be unavailable for the 1% of the time at most

### 2.5 Assumptions and dependencies
[TODO]

---

## 3. Requirements
The following section will distinguish between Functional Requirements (FR, 3.1) and Non-functional requirements (NFR, 3.2).

### 3.1 Functional Requirements
[TODO]
- 3.1.01 FR: The system shall allow users to create an account using email or social authentication (Google, Meta, Apple).
- 3.1.02 FR: The system shall allow users to share an image (ideally of food) with .
- 3.1.03 FR: The system should be able to recognize the food types in the image sent by the user with a maximum delay of 2 seconds.
- 3.1.04 FR: The system should write a .JSON file called "ingredients.json" with the types of food recognized.
- 3.1.05 FR: The system should be able to send the file called "ingredients.json" to a defined online Large Language Model (LLM), e.g. OpenAI GPT-5.
- 3.1.06 FR: The system should be able to send the file called "ingredients.json" to the front-end in order to be shown to the user.
- 3.1.07 FR: The LLM model should write the recipe into a .JSON file called "recipe.json"
- 3.1.08 FR: The file called "recipe.json" should be sent to the front-end and shown to the user.
- 3.1.09 FR: The system shall allow users to give a feedback w.r.t. the recipe recieved.
- 3.1.10 FR: The system shall log the user activities for analytic purpose, with a dedicated buffer for storing the user feedbacks. 
- 3.1.11 FR: The system shall report the administrators of the project for inappropriate content, e.g. images not regarding food (TBD).
- 3.1.12 FR: The system should block the user in case of multiple inappropriate content. (TBD)

### 3.2 Non-Functional Requirements
[TODO]
- 3.2.1 NFR: The system shall comply with the GDPR standards for user data privacy.
- 3.2.2 NFR: The system shall ask the user for cookies usage, using the product CookieBot.
- 3.2.3 NFR: The system shall be made up by two components: a front-end and a back-end.
- 3.2.3.1 NFR: The frontend shall be written in TypeScript programming Language in order to be compatible with the major search engines.
- 3.2.3.2 NFR: The frontend shall follow the standard guidelines for a frontend project structure.
- 3.2.3.3 NFR: The Backend shall be written in Python programming Language in order to be compatible with the standard ML modules.
- 3.2.3.4 NFR: Front-end and back-end shall communicate using the framework Django.
- 3.2.3.5 NFR: The communication between front-end and back-end shall be ensured by the Code Generator Swagger.
- 3.2.4 NFR: The back-end should be able to run a Machine Learning component, ensuring communication and logging between the two.
- 3.2.4.1 NFR: The ML component shall made up by different sub-sections here described.
- 3.2.4.2 NFR: The first ML subsection shall be an Orchestrator Engine (OE), whose task is to call the other subsequent ML models, starting with the so-called "Principal Model".
- 3.2.4.3 NFR: The second ML subsection is the so-called "Principal Model" should be a fine-tuned YOLO8 or YOLO11 model, able to recognize general categories (meat, fish, vegetables, fruit, drinks, cheese, cold cuts) of food in an image. 
- 3.2.4.4 NFR: The recognized portions of the image should be cropped and sent to the OE, as well as the label of the recogized food in the cropped image.
- 3.2.4.5 NFR: The cropped image shall be sent from the OE to the corresponding ML module specifically trained with that category of food. E.g. in the image is recognized a cheese, than will be called the model specifically trained on cheese.
- 3.2.4.6 NFR: The food-specific model will recover the specific type of food in the cropped image it received. The results should be written into a unique JSON file "food.json".
- 3.2.4.7 NFR: The last sub-system should allow to integrate through an API system a LLM from XYZQUELLACHECOSTAMENO. The API should be saved into the secrets session.
- 3.2.4.8 NFR: The LLM should be initialize with a prompt specifing the project and the answer it should provide. In our case, it should read the file "Food.json" and write a recipe based on the food in the content of the file. Some examples and negative prompts can be included in the prompt as well.
- 3.2.4.9 NFR: The "food.json" file should be sent to the LLM subsystem specifically initialized; the recipe should be written into a "recipe.json" file.
- 3.2.5 NFR: The file "recipe.json" should be sent to the frontend and the content shown.


## 4. Project Architecture
[TODO]
### 4.1 Training, Validation, Deployment, Monitoring


## 5. Risk Analysis
[TODO]

## 6. Appendices & Resources
[TODO]
