from rest_framework.test import APITestCase
from rest_framework import status

from locations.models import Location
from characters.models import Character


class TestLocationViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.main_character = Character.objects.create(
            name="Walter White", date_of_birth="1970-11-01", occupation="Teacher"
        )

    # Tests that a single location can be retrieved by its ID.
    def test_retrieve_location_successfully(self):
        """
        Given a location exists in the database
        When a GET request is made to retrieve that location by its ID
        Then the response should have a status code of 200 and contain the location's data
        """

        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["character"] == 1
        assert response.data["timestamp"] == "2020-01-01T00:00:00Z"
        assert response.data["lat"] == "10.000000"
        assert response.data["lon"] == "10.000000"

    # Tests that a list of locations can be retrieved successfully.
    def test_list_locations_successfully(self):
        """
        Given multiple locations exist in the database
        When a GET request is made to list locations
        Then the response should have a status code of 200 and contain a list of locations data
        """
        # Given
        Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        Location.objects.create(
            character=self.main_character,
            timestamp="2022-01-01T00:00:00.000Z",
            lat="50",
            lon="50",
        )
        url = "/locations/"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["character"] == 1
        assert response.data[0]["timestamp"] == "2020-01-01T00:00:00Z"
        assert response.data[0]["lat"] == "10.000000"
        assert response.data[0]["lon"] == "10.000000"

    # Tests that an error is returned when invalid query parameters are used to near locations.
    def test_near_locations_with_invalid_query_params(self):
        """
        Given multiple locations exist in the database
        When a GET request is made to locations/near with invalid query parameters
        Then the response should have a status code of 422 and contain an error message
        """
        # Given
        Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = "/locations/near/?character=1&ascending=0"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "The query parameters `coordinates` and `distance` are obligatory. `coordinates` accepts a `latitude,longitude` pair. `distance` accepts any value >= 0"
            in response.data["detail"]
        )

    # Tests that an error is returned when invalid data is used to create a location.
    def test_create_location_with_invalid_data(self):
        """
        Given invalid location data
        When a POST request is made to create a location
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        data = {"character": "1"}

        # When
        response = self.client.post("/locations/", data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field is required." in response.data["timestamp"]

    # Tests that a location can be created successfully.
    def test_create_location_successfully(self):
        """
        Given valid location data
        When a POST request is made to create a location
        Then the response should have a status code of 201 and contain the location's data
        """
        # Given
        data = {
            "character": 1,
            "timestamp": "2023-01-01T18:59:00.618000Z",
            "lat": "50.00",
            "lon": "40.00",
        }

        # When
        response = self.client.post("/locations/", data=data)

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["character"] == 1
        assert response.data["timestamp"] == "2023-01-01T18:59:00.618000Z"
        assert response.data["lat"] == "50.000000"
        assert response.data["lon"] == "40.000000"

    # Tests that a location can be updated successfully.
    def test_update_location_successfully(self):
        """
        Given a location exists in the database
        When a PUT request is made to update that location with valid data
        Then the response should have a status code of 200 and contain the updated location's data
        """
        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"
        data = {
            "character": 1,
            "timestamp": "2023-01-01T18:59:00.618000Z",
            "lat": "50.00",
            "lon": "40.00",
        }

        # When
        response = self.client.put(url, data=data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["character"] == 1
        assert response.data["timestamp"] == "2023-01-01T18:59:00.618000Z"
        assert response.data["lat"] == "50.000000"
        assert response.data["lon"] == "40.000000"

    # Tests that a location can be partially updated successfully.
    def test_partial_update_location_successfully(self):
        """
        Given a location exists in the database
        When a PATCH request is made to partially update that location with valid data
        Then the response should have a status code of 200 and contain the updated location's data
        """
        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"
        data = {"lat": "20"}

        # When
        response = self.client.patch(url, data=data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["character"] == 1
        assert response.data["timestamp"] == "2020-01-01T00:00:00Z"
        assert response.data["lat"] == "20.000000"
        assert response.data["lon"] == "10.000000"

    # Tests that a location can be deleted successfully.
    def test_delete_location_successfully(self):
        """
        Given a location exists in the database
        When a DELETE request is made to delete that location
        Then the response should have a status code of 204 and the location should no longer exist in the database
        """
        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"

        # When
        response = self.client.delete(url)

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Location.objects.filter(id=location.id).exists()

    # Tests that an error is returned when invalid data is used to update a location.
    def test_update_location_with_invalid_data(self):
        """
        Given a location exists in the database
        When a PUT request is made to update that location with invalid data
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"
        data = {
            "character": "",
            "timestamp": "2023-01-01T18:59:00.618000Z",
            "lat": "50.00",
            "lon": "40.00",
        }

        # When
        response = self.client.put(url, data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field may not be null." in response.data["character"]

    # Tests that an error is returned when invalid data is used to partially update a location.
    def test_partial_update_location_with_invalid_data(self):
        """
        Given a location exists in the database
        When a PATCH request is made to partially update that location with invalid data
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        location = Location.objects.create(
            character=self.main_character,
            timestamp="2020-01-01T00:00:00Z",
            lat="10",
            lon="10",
        )
        url = f"/locations/{location.id}/"
        data = {"lat": ""}

        # When
        response = self.client.patch(url, data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "A valid number is required." in response.data["lat"]

    # Tests that an error is returned when attempting to retrieve a non-existent location.
    def test_retrieve_non_existent_location(self):
        """
        Given no location exists in the database with the given ID
        When a GET request is made to retrieve that location by its ID
        Then the response should have a status code of 404 and contain an error message
        """
        # Given
        url = "/locations/999/"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Not found." in response.data["detail"]
