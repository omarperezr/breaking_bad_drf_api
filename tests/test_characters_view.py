from rest_framework.test import APITestCase
from rest_framework import status

from characters.models import Character


class TestCharacterViewSet(APITestCase):
    # Tests that a single character can be retrieved by its ID.
    def test_retrieve_character_successfully(self):
        """
        Given a character exists in the database
        When a GET request is made to retrieve that character by its ID
        Then the response should have a status code of 200 and contain the character's data
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "John Doe"
        assert response.data["date_of_birth"] == "1990-01-01"
        assert response.data["occupation"] == "Teacher"

    # Tests that a list of characters can be retrieved successfully.
    def test_list_characters_successfully(self):
        """
        Given multiple characters exist in the database
        When a GET request is made to list characters with valid query parameters
        Then the response should have a status code of 200 and contain a list of characters' data
        """
        # Given
        Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher", is_suspect=True)
        Character.objects.create(name="Jane Smith", date_of_birth="1995-05-05", occupation="Doctor")
        url = "/characters/?orderBy=date_of_birth&ascending=1&name=John&suspect=true"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "John Doe"
        assert response.data[0]["date_of_birth"] == "1990-01-01"
        assert response.data[0]["occupation"] == "Teacher"
        assert response.data[0]["is_suspect"] is True

    # Tests that an error is returned when invalid query parameters are used to list characters.
    def test_list_characters_with_invalid_query_params(self):
        """
        Given multiple characters exist in the database
        When a GET request is made to list characters with invalid query parameters
        Then the response should have a status code of 422 and contain an error message
        """
        # Given
        Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = "/characters/?name=John&sort=true"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "The query parameters `orderBy` and `ascending` are obligatory" in response.data["detail"]

    # Tests that an error is returned when invalid data is used to create a character.
    def test_create_character_with_invalid_data(self):
        """
        Given invalid character data
        When a POST request is made to create a character
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        data = {"name": "John Doe", "date_of_birth": "1990-01-01"}

        # When
        response = self.client.post("/characters/", data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field is required." in response.data["occupation"]

    # Tests that a character can be created successfully.
    def test_create_character_successfully(self):
        """
        Given valid character data
        When a POST request is made to create a character
        Then the response should have a status code of 201 and contain the character's data
        """
        # Given
        data = {"name": "John Doe", "date_of_birth": "1990-01-01", "occupation": "Teacher"}

        # When
        response = self.client.post("/characters/", data=data)

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "John Doe"
        assert response.data["date_of_birth"] == "1990-01-01"
        assert response.data["occupation"] == "Teacher"
        assert response.data["is_suspect"] is False

    # Tests that a character can be updated successfully.
    def test_update_character_successfully(self):
        """
        Given a character exists in the database
        When a PUT request is made to update that character with valid data
        Then the response should have a status code of 200 and contain the updated character's data
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"
        data = {"name": "Jane Smith", "date_of_birth": "1995-05-05", "occupation": "Doctor"}

        # When
        response = self.client.put(url, data=data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Jane Smith"
        assert response.data["date_of_birth"] == "1995-05-05"
        assert response.data["occupation"] == "Doctor"
        assert response.data["is_suspect"] is False

    # Tests that a character can be partially updated successfully.
    def test_partial_update_character_successfully(self):
        """
        Given a character exists in the database
        When a PATCH request is made to partially update that character with valid data
        Then the response should have a status code of 200 and contain the updated character's data
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"
        data = {"occupation": "Doctor"}

        # When
        response = self.client.patch(url, data=data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "John Doe"
        assert response.data["date_of_birth"] == "1990-01-01"
        assert response.data["occupation"] == "Doctor"
        assert response.data["is_suspect"] is False

    # Tests that a character can be deleted successfully.
    def test_delete_character_successfully(self):
        """
        Given a character exists in the database
        When a DELETE request is made to delete that character
        Then the response should have a status code of 204 and the character should no longer exist in the database
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"

        # When
        response = self.client.delete(url)

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Character.objects.filter(id=character.id).exists()

    # Tests that an error is returned when invalid data is used to update a character.
    def test_update_character_with_invalid_data(self):
        """
        Given a character exists in the database
        When a PUT request is made to update that character with invalid data
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"
        data = {"name": "", "date_of_birth": "1990-01-01", "occupation": "Teacher"}

        # When
        response = self.client.put(url, data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field may not be blank." in response.data["name"]

    # Tests that an error is returned when invalid data is used to partially update a character.
    def test_partial_update_character_with_invalid_data(self):
        """
        Given a character exists in the database
        When a PATCH request is made to partially update that character with invalid data
        Then the response should have a status code of 400 and contain an error message
        """
        # Given
        character = Character.objects.create(name="John Doe", date_of_birth="1990-01-01", occupation="Teacher")
        url = f"/characters/{character.id}/"
        data = {"name": ""}

        # When
        response = self.client.patch(url, data=data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field may not be blank." in response.data["name"]

    # Tests that an error is returned when attempting to retrieve a non-existent character.
    def test_retrieve_non_existent_character(self):
        """
        Given no character exists in the database with the given ID
        When a GET request is made to retrieve that character by its ID
        Then the response should have a status code of 404 and contain an error message
        """
        # Given
        url = "/characters/999/"

        # When
        response = self.client.get(url)

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Not found." in response.data["detail"]
