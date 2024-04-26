import requests
import math


class Vehicle:
    def __init__(
            self,
            name,
            model,
            year,
            color,
            price,
            latitude,
            longitude,
            id=None
            ) -> None:
        self.id = id
        self.name = name
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self) -> str:
        return (f'<Vehicle: {self.name} {self.model} '
                f'{self.year} {self.color} {self.price}>')


class VehicleManager:
    def __init__(self, url) -> None:
        self.url = url + '/vehicles'

    def json_to_vehicle(self, data) -> Vehicle:
        return Vehicle(
            id=data['id'],
            name=data['name'],
            model=data['model'],
            year=data['year'],
            color=data['color'],
            price=data['price'],
            latitude=data['latitude'],
            longitude=data['longitude']
            )

    def vehicle_to_json(self, vehicle) -> dict:
        return {
            'id': vehicle.id,
            'name': vehicle.name,
            'model': vehicle.model,
            'year': vehicle.year,
            'color': vehicle.color,
            'price': vehicle.price,
            'latitude': vehicle.latitude,
            'longitude': vehicle.longitude
        }

    def distance_calculation(self, lat1, lot1, lat2, lot2) -> float:
        R = 6371.0

        r_lat1 = math.radians(lat1)
        r_lon1 = math.radians(lot1)

        r_lat2 = math.radians(lat2)
        r_lon2 = math.radians(lot2)

        dlat = r_lat2 - r_lat1
        dlon = r_lon2 - r_lon1

        a = (math.sin(dlat / 2)**2 + math.cos(r_lat1) *
             math.cos(r_lat2) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c * 1000

        return distance

    def get_vehicles(self) -> list[Vehicle]:
        request = requests.get(url=self.url)
        if request.status_code == 200:
            result = []
            for data in request.json():
                result.append(self.json_to_vehicle(data))
            return result
        return request.json()

    def filter_vehicles(self, params) -> list[Vehicle]:
        all_vehicles = self.get_vehicles()
        result = [vehicle for vehicle in all_vehicles if
                  (not 'id' in params or vehicle.id == params['id']) and
                  (not 'name' in params or vehicle.name == params['name']) and
                  (not 'model' in params or vehicle.model == params['model']) and
                  (not 'year' in params or vehicle.year == params['year']) and
                  (not 'color' in params or vehicle.color == params['color']) and
                  (not 'price' in params or vehicle.price == params['price']) and
                  (not 'latitude' in params or vehicle.latitude == params['latitude']) and
                  (not 'longitude' in params or vehicle.longitude == params['longitude'])
                  ]
        return result

    def get_vehicle(self, vehicle_id) -> Vehicle:
        request = requests.get(url=self.url+f'/{vehicle_id}')
        if request.status_code == 200:
            return self.json_to_vehicle(request.json())
        return request.json()

    def add_vehicle(self, vehicle: Vehicle) -> Vehicle:
        data = self.vehicle_to_json(vehicle=vehicle)
        request = requests.post(url=self.url, data=data)
        if request.status_code == 201:
            new_vehicle = self.json_to_vehicle(data=request.json())
            return new_vehicle
        return request.json()

    def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        data = self.vehicle_to_json(vehicle=vehicle)
        request = requests.put(url=self.url + f'/{vehicle.id}', data=data)
        if request.status_code == 200:
            new_vehicle = self.json_to_vehicle(data=request.json())
            return new_vehicle
        return request.json()

    def delete_vehicle(self, id) -> None:
        request = requests.delete(url=self.url + f'/{id}')
        if request.status_code == 404:
            return request.json()

    def get_distance(self, id1, id2) -> float:
        data1 = requests.get(url=self.url + f'/{id1}').json()
        data2 = requests.get(url=self.url + f'/{id2}').json()
        vehicle1 = self.json_to_vehicle(data1)
        vehicle2 = self.json_to_vehicle(data2)
        return self.distance_calculation(
            lat1=vehicle1.latitude,
            lot1=vehicle1.longitude,
            lat2=vehicle2.latitude,
            lot2=vehicle2.longitude
        )

    def get_nearest_vehicle(self, id) -> Vehicle:
        current_vehicle = self.get_vehicle(vehicle_id=id)
        all_vehicles = self.get_vehicles()
        nearest_vehicle = None
        min_distance = 0
        for vehicle in all_vehicles:
            if current_vehicle.id == vehicle.id:
                continue
            distance = self.distance_calculation(
                current_vehicle.latitude,
                current_vehicle.longitude,
                vehicle.latitude,
                vehicle.longitude
            )
            if min_distance == 0 or distance < min_distance:
                min_distance = distance
                nearest_vehicle = vehicle

        return nearest_vehicle
