# liine_take_home

This project is to demonstrate a Python API for providing a list of restaurants
open at a given datetime query string.

## Components:
#### ETL - Extract restaurant info, Transform into easy lookup object, Load into sql db
#### DB - sqlite3 db managed by sqlalchemy to simplify query of restaurants open
#### Flask app - provides the endpoints for getting the resource

**Endpoints**
----
**Get Open Restaurants**
* **URL**

  /

* **Method:**

  `GET` | `POST`
  
*  **URL Params**

   **Required:**
 
   `datetime=[string]`

   **Optional:**
 
   `datetime=[integer]` AKA timestamp

* **Data Params**

  `{'datetime': [string | integer]}`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'success': True, 'data': data=[array[string]]}`
 
* **Error Response:**

  * **Code:** 400 <br />
    **Content:** `{'success': False, 'message': 'human readable error'}`
  

* **Sample Call:**

  /?datetime=12/15/2022 00:48:15


**Reload Restaurant Data**
* **URL**

  /refresh

* **Method:**

  `POST`
  
*  **URL Params**<br />
    None

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'success': True}`
 
* **Error Response:**

  * **Code:** 501 <br />
    **Content:** `{'success': False}`
  

* **Sample Call:**

  /refresh

* **Notes:**

    This endpoint is expecting a pipeline has already placed the restaurants.csv in the expected file path.




