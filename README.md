🚀 SpeedRide Car Rental System (FastAPI)

📌 Project Overview
This is a backend system built using FastAPI for managing car rental operations like car management, rentals, returns, and browsing.

----

🔑 Features
REST APIs with FastAPI
Pydantic data validation
Car management system (Add, Update, Delete)
Rental creation and return workflow
Cost calculation logic (discount, insurance, driver)
Availability tracking
Search functionality
Sorting and filtering
Pagination
Combined browse API

----

🔗 API Functionalities

🟢 Cars APIs
GET /cars → Get all cars
GET /cars/{car_id} → Get car by ID
GET /cars/summary → Cars summary
GET /cars/filter → Filter cars
GET /cars/search → Search cars
GET /cars/sort → Sort cars
GET /cars/page → Pagination
GET /cars/browse → Combined search + filter + sort + pagination
GET /cars/unavailable → Get unavailable cars
POST /cars → Add new car
PUT /cars/{car_id} → Update car
DELETE /cars/{car_id} → Delete car

----

🟡 Rentals APIs
POST /rentals → Create rental
GET /rentals → Get all rentals
GET /rentals/{rental_id} → Get rental by ID
GET /rentals/active → Get active rentals
GET /rentals/by-car/{car_id} → Rental history by car
GET /rentals/search → Search rentals
GET /rentals/sort → Sort rentals
GET /rentals/page → Paginate rentals
POST /return/{rental_id} → Return rented car

----

🛠️ Tech Stack
Python
FastAPI
Uvicorn
Pydantic

----

▶️ How to Run

1. Clone the repository
https://github.com/gvd6714-ctrl/Car_Rental_Service

2. Install dependencies
pip install -r requirements.txt

3. Run server
uvicorn main:app --reload

4. Open in browser
http://127.0.0.1:8000/docs

----

📸 Screenshots
All endpoints are tested in Swagger UI. Screenshots are available in Output Screenshots folder.

----

📂 Project Structure

main.py  
requirements.txt  
README.md  
Output Screenshots 

----

🙌 Acknowledgement
This project was built as part of internship training. Grateful for the learning opportunity at Innomatics Research Labs.
