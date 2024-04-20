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
