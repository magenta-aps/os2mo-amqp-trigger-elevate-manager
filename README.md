<!--
SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->
# OS2mo-amqp-trigger-elevate-manager

OS2MO trigger receiver. This is an AMQP service that, using RabbitMQ, listens in on events made in MO to manager positions. The listener triggers a series of events, whenever
a new manager has been created or edited. The events are handled sequentially as follows:
 - _A create/edit to a manager position has been made_
 - _Make a GraphQL query to MO on the person created/edited as manager_
 - _Pull relevant UUIDs from the manager and person objects_
 - _Make a GraphQL query to perform check for already existing managers for the position created/edited_
 - _If any existing managers are presently occupying the position, terminate these firstly_
 - _Move the persons engagement, who has been made into a manager, to be in the same organisation unit as the managers position_

## Code Responsibilities


| File            | Functionality                                                              |
|-----------------|----------------------------------------------------------------------------|
| `main.py`       | Configuration and initialization of AMQP listener.                         |
| `main.py`       | Listening for incoming AMQP events                                         |
| `mo.py`         | Creating GraphQL                                                           |
| `mo.py`         | Making queries to MO in order to retrieve relevant data                    |
| `mo.py`         | Making mutations to MO in order to terminate and move relevant engagements |
| `log.py`        | Setting up logging                                                         |
| `events.py`     | Handlings each specific call in this integration via an event processor    |
| `exceptions.py` | # TODO Handle GraphQL exceptions                                           |
| `models/`       | Defining model instances generated automatically by QuickType              |
| `tests/`        | Unit-testing                                                               |
