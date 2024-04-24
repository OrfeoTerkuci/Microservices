# Microservices

## Roadmap

- [ ] Decompose into microservices: Backend
  - [ ] Authentication
    - [ ] Create user model
    - [ ] Register
    - [ ] Login: `username`, `password`
- [ ] Events
  - [ ] Create event model
  - [ ] Implement event invitation system
  - [ ] Display event invitations for a user
  - [ ] Allow user to respond to event invitation: `accept`, `decline`, `maybe`
  - [ ] Display participants and maybe participants for an event
  - [ ] Implement public events page
  - [ ] Allow user to indicate participation for public events
- [ ] Calendar & Sharing
  - [ ] Create calendar model
  - [ ] Create a calendar for a user on registration
  - [ ] Display the events that a user is (maybe) participating in
  - [ ] Do not display invites that have not yet been responded to
  - [ ] Allow user to share calendar with other users (asymmetric sharing)
- [ ] All services fail gracefully
  - [ ] Authentication service fails gracefully
  - [ ] Events service fails gracefully
  - [ ] Calendar service fails gracefully
  - [ ] Sharing service fails gracefully
- [ ] Databases
  - [ ] Use a different database for each service
    - [ ] Database for authentication service
    - [ ] Database for events service
    - [ ] Database for calendar service
    - [ ] Database for invitation service
  - [ ] Create a wrapper for database access
    - [ ] Implement database access for authentication service
    - [ ] Implement database access for events service
    - [ ] Implement database access for calendar service
    - [ ] Implement database access for invitation service
  - [ ] Ensure that foreign keys are implemented at the application level
- [ ] Frontend
  - [ ] Create a frontend for the application
  - [ ] Use the frontend to interact with the services
    - [ ] Register
    - [ ] Login
    - [ ] Create event
    - [ ] Respond to event invitation
    - [ ] Display events
    - [ ] Display calendar
    - [ ] Share calendar
    - [ ] Display shared calendars
    - [ ] Display participants for an event
    - [ ] Display maybe participants for an event
    - [ ] Display public events
    - [ ] Indicate participation for public events
- [ ] Deliverables
  - [ ] Run script `./run.sh` that starts all services
  - [ ] Report


## Application-Level Foreign Keys in Microservices Architecture

Sure, here are some tips for implementing application-level foreign keys in a microservices architecture:

1. **Consistency Checks**: Before performing any operation that would violate a foreign key constraint in a monolithic application, your service should make a request to the service that owns the data to check if the operation is valid. For example, if you have a `Orders` service and a `Customers` service, before creating an order, the `Orders` service should check if the customer exists in the `Customers` service.

2. **Error Handling**: Your services should be able to handle the case where a referenced entity does not exist. This could be returning an error to the client, or it could involve some form of compensation transaction to ensure data consistency.

3. **Data Duplication**: In some cases, it might make sense to duplicate some data across services. This can reduce the number of cross-service calls and improve performance. However, this comes with its own challenges in keeping the duplicated data in sync.

4. **Asynchronous Communication**: Consider using asynchronous communication (like message queues) for inter-service communication. This can help to decouple your services further and can improve performance and reliability.

5. **Caching**: To reduce the number of cross-service calls, you could cache the results of consistency checks. However, this introduces the challenge of cache invalidation, which can be tricky to get right.

6. **Monitoring and Alerting**: Since you're now relying on your application logic to enforce data consistency, it's important to have robust monitoring and alerting in place to notify you of any issues as soon as possible.
