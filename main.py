from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="🚗 SpeedRide Car Rental API",
    description="Manage cars, rentals, returns, and browsing",
    version="1.0"
)

# ===================== DAY 1 =====================

# Home Route
@app.get("/", tags=["General"], summary="Home route")
def home():
    return {"message": "Welcome to SpeedRide Car Rentals"}

# Cars Data
cars = [
    {"id": 1, "model": "Swift", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1200, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "model": "City", "brand": "Honda", "type": "Sedan", "price_per_day": 2500, "fuel_type": "Petrol", "is_available": True},
    {"id": 3, "model": "Creta", "brand": "Hyundai", "type": "SUV", "price_per_day": 3000, "fuel_type": "Diesel", "is_available": True},
    {"id": 4, "model": "Fortuner", "brand": "Toyota", "type": "SUV", "price_per_day": 5000, "fuel_type": "Diesel", "is_available": True},
    {"id": 5, "model": "Tesla Model 3", "brand": "Tesla", "type": "Luxury", "price_per_day": 7000, "fuel_type": "Electric", "is_available": True},
    {"id": 6, "model": "i20", "brand": "Hyundai", "type": "Hatchback", "price_per_day": 1500, "fuel_type": "Petrol", "is_available": True},
]

# GET all cars
@app.get("/cars", tags=["Cars"])
def get_cars():
    available = [c for c in cars if c["is_available"]]
    return {
        "total": len(cars),
        "available_count": len(available),
        "cars": cars
    }

# Cars Summary 
@app.get("/cars/summary", tags=["Cars"])
def cars_summary():
    types = {}
    fuel = {}

    for c in cars:
        types[c["type"]] = types.get(c["type"], 0) + 1
        fuel[c["fuel_type"]] = fuel.get(c["fuel_type"], 0) + 1

    cheapest = min(cars, key=lambda x: x["price_per_day"])
    expensive = max(cars, key=lambda x: x["price_per_day"])

    return {
        "total": len(cars),
        "available": len([c for c in cars if c["is_available"]]),
        "by_type": types,
        "by_fuel": fuel,
        "cheapest": cheapest,
        "most_expensive": expensive
    }

# Rentals Data
rentals = []
rental_counter = 1

# GET rentals
@app.get("/rentals", tags=["Rentals"])
def get_rentals():
    return {"total": len(rentals), "rentals": rentals}

# ===================== DAY 2 =====================

class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license_number: str = Field(..., min_length=8)
    insurance: bool = False
    driver_required: bool = False

class NewCar(BaseModel):
    model: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    type: str = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type: str = Field(..., min_length=2)
    is_available: bool = True

# ===================== DAY 3 =====================

# Helper: find car
def find_car(car_id):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None

# Cost calculation
def calculate_rental_cost(price, days, insurance, driver):
    base = price * days
    discount = 0

    if days >= 15:
        discount = 0.25 * base
    elif days >= 7:
        discount = 0.15 * base

    insurance_cost = 500 * days if insurance else 0
    driver_cost = 800 * days if driver else 0

    total = base - discount + insurance_cost + driver_cost

    return base, discount, insurance_cost, driver_cost, total

# Filter cars
@app.get("/cars/filter", tags=["Cars"])
def filter_cars(
    type: Optional[str] = None,
    brand: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = cars

    if type is not None:
        result = [c for c in result if c["type"].lower() == type.lower()]

    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]

    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]

    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]

    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return {"count": len(result), "cars": result}

# ===================== DAY 4 =====================

# Add new car
@app.post("/cars", status_code=status.HTTP_201_CREATED, tags=["Cars"])
def add_car(car: NewCar):
    for c in cars:
        if c["model"].lower() == car.model.lower() and c["brand"].lower() == car.brand.lower():
            raise HTTPException(400, "Car already exists")

    new_id = len(cars) + 1
    new_car = car.dict()
    new_car["id"] = new_id
    cars.append(new_car)

    return new_car

# Update car
@app.put("/cars/{car_id}", tags=["Cars"])
def update_car(
    car_id: int,
    price_per_day: Optional[int] = None,
    is_available: Optional[bool] = None
):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    if price_per_day is not None:
        if price_per_day <= 0:
            raise HTTPException(400, "price_per_day must be greater than 0")
        car["price_per_day"] = price_per_day

    if is_available is not None:
        car["is_available"] = is_available

    return car

# Delete car
@app.delete("/cars/{car_id}", tags=["Cars"])
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    for r in rentals:
        if r["car_id"] == car_id and r["status"] == "active":
            raise HTTPException(400, "Car has active rental")

    cars.remove(car)
    return {"message": "Car deleted"}

# ===================== DAY 5 =====================

# Create rental
@app.post("/rentals", tags=["Rentals"])
def create_rental(req: RentalRequest):
    global rental_counter

    car = find_car(req.car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    if not car["is_available"]:
        raise HTTPException(400, "Car not available")

    base, discount, ins, driver, total = calculate_rental_cost(
        car["price_per_day"], req.days, req.insurance, req.driver_required
    )

    rental = {
        "rental_id": rental_counter,
        "customer_name": req.customer_name,
        "car_id": req.car_id,
        "car": f"{car['brand']} {car['model']}",
        "days": req.days,
        "insurance": req.insurance,
        "driver_required": req.driver_required,
        "base_cost": base,
        "discount": discount,
        "insurance_cost": ins,
        "driver_cost": driver,
        "total_cost": total,
        "status": "active"
    }

    rentals.append(rental)
    car["is_available"] = False
    rental_counter += 1

    return rental

# Return car
@app.post("/return/{rental_id}", tags=["Rentals"])
def return_car(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            r["status"] = "returned"
            car = find_car(r["car_id"])
            car["is_available"] = True
            return r

    raise HTTPException(404, "Rental not found")

# Active rentals
@app.get("/rentals/active", tags=["Rentals"])
def active_rentals():
    return [r for r in rentals if r["status"] == "active"]

# ===================== TASK 19 RENTALS =====================


# Search rentals by customer_name (case-insensitive)
@app.get("/rentals/search", tags=["Rentals"])
def search_rentals(keyword: str):
    result = [r for r in rentals if keyword.lower() in r["customer_name"].lower()]
    return {"total_found": len(result), "rentals": result}

# Sort rentals by total_cost or days (ascending)
@app.get("/rentals/sort", tags=["Rentals"])
def sort_rentals(sort_by: str = "total_cost"):
    allowed_fields = ["total_cost", "days"]
    if sort_by not in allowed_fields:
        raise HTTPException(400, f"Invalid sort_by. Allowed values: {allowed_fields}")

    return sorted(rentals, key=lambda x: x[sort_by])

# Paginate rentals list
@app.get("/rentals/page", tags=["Rentals"])
def paginate_rentals(page: int = 1, limit: int = 3):
    if page <= 0 or limit <= 0:
        raise HTTPException(400, "page and limit must be greater than 0")

    total = len(rentals)
    start = (page - 1) * limit
    end = start + limit
    paged_rentals = rentals[start:end]

    total_pages = (total + limit - 1) // limit  

    return {
        "total_rentals": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "rentals": paged_rentals
    }

# Get rental by ID
@app.get("/rentals/{rental_id}", tags=["Rentals"])
def get_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    raise HTTPException(404, "Rental not found")

# Rental history by car
@app.get("/rentals/by-car/{car_id}", tags=["Rentals"])
def rentals_by_car(car_id: int):
    car_rentals = [r for r in rentals if r["car_id"] == car_id]
    if not car_rentals:
        raise HTTPException(404, "No rentals found for this car")
    return {"count": len(car_rentals), "rentals": car_rentals}

# Unavailable cars
@app.get("/cars/unavailable", tags=["Cars"])
def unavailable_cars():
    result = [c for c in cars if not c["is_available"]]
    return {"count": len(result), "cars": result}

# ===================== DAY 6 =====================

# Search cars
@app.get("/cars/search", tags=["Cars"])
def search_cars(keyword: str):
    result = [
        c for c in cars
        if keyword.lower() in c["model"].lower()
        or keyword.lower() in c["brand"].lower()
        or keyword.lower() in c["type"].lower()
    ]
    return {"total_found": len(result), "cars": result}

# Sort cars
@app.get("/cars/sort", tags=["Cars"])
def sort_cars(sort_by: str = "price_per_day"):
    allowed_fields = ["price_per_day", "brand", "type"]
    if sort_by not in allowed_fields:
        raise HTTPException(400, f"Invalid sort_by. Allowed values: {allowed_fields}")
    
    return sorted(cars, key=lambda x: x[sort_by])

# Pagination
@app.get("/cars/page", tags=["Cars"])
def paginate(page: int = 1, limit: int = 3):
    if page <= 0 or limit <= 0:
        raise HTTPException(400, "page and limit must be greater than 0")
    
    total = len(cars)
    start = (page - 1) * limit
    end = start + limit
    paged_cars = cars[start:end]

    total_pages = (total + limit - 1) // limit  # ceil division

    return {
        "total_cars": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "cars": paged_cars
    }

@app.get("/cars/browse", tags=["Cars"])
def browse_cars(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = cars

    # 1. Search (keyword)
    if keyword:
        result = [
            c for c in result
            if keyword.lower() in c["model"].lower()
            or keyword.lower() in c["brand"].lower()
            or keyword.lower() in c["type"].lower()
        ]

    # 2. Filters
    if type:
        result = [c for c in result if c["type"].lower() == type.lower()]

    if fuel_type:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]

    if max_price:
        result = [c for c in result if c["price_per_day"] <= max_price]

    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    # 3. Sorting
    allowed_sort_fields = ["price_per_day", "brand", "type"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(400, f"Invalid sort_by. Allowed: {allowed_sort_fields}")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # 4. Pagination
    if page <= 0 or limit <= 0:
        raise HTTPException(400, "page and limit must be greater than 0")

    total = len(result)
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "total_results": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "cars": paginated
    }

# ===================== VARIABLE ROUTES =====================

@app.get("/cars/{car_id}", tags=["Cars"])
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return car