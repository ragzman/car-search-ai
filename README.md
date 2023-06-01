# car-search-ai

This repository contains the code for a car search AI application.

## Installation

To set up the application, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/ragzman/car-search-ai.git
   ```

2. Change into the project directory:

   ```bash
   cd car-search-ai
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following commands:

1. Start the backend server:

   ```bash
   uvicorn main:app --reload
   ```

   This will start the backend server using [Uvicorn](https://www.uvicorn.org/) with live reloading enabled.

2. Open a new terminal or command prompt and change into the frontend directory:

   ```bash
   cd frontend
   ```

3. Start the frontend development server:

   ```bash
   ng serve
   ```

   This will start the frontend development server using [Angular](https://angular.io/) and serve the application.

4. Open your web browser and navigate to [http://localhost:4200](http://localhost:4200) to access the application.
