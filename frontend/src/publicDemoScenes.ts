// Generated from backend.negotiation_engine; run python -m scripts.export_public_demo.
export const publicDemoScenes = {
  "initial": {
    "status": "idle",
    "events": [],
    "pending_approval": null,
    "outcome": null,
    "profiles": [
      {
        "name": "Alice",
        "role": "Photography & comfort",
        "public_goals": [
          "Oceanfront stay",
          "Scenery and photo stops",
          "Key West coast"
        ]
      },
      {
        "name": "Bob",
        "role": "Food & nightlife",
        "public_goals": [
          "Cuban cuisine",
          "Miami Beach nightlife"
        ]
      },
      {
        "name": "Carol",
        "role": "Culture & rest",
        "public_goals": [
          "Vizcaya Museum",
          "Hemingway Home"
        ]
      }
    ],
    "step_count": 0,
    "decision": null,
    "simulation": "Scripted simulation · fictional sample data",
    "mode": "scripted"
  },
  "progression": [
    {
      "status": "running",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        }
      ],
      "pending_approval": null,
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 1,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    },
    {
      "status": "running",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        },
        {
          "event_id": "E02",
          "actor": "Carol",
          "action": "REJECT",
          "proposal": {
            "departure": "07:00"
          },
          "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
          "policy_outcome": {
            "status": "blocked",
            "code": "HARD_CONSTRAINT_VIOLATION",
            "explanation": "Carol requires group departures at or after 09:30."
          },
          "step": 2
        },
        {
          "event_id": "E03",
          "actor": "Carol",
          "action": "COUNTER",
          "proposal": {
            "departure": "09:30",
            "destination": "Key West"
          },
          "public_message": "Let’s leave together at 09:30.",
          "policy_outcome": {
            "status": "allowed",
            "code": "GROUP_DEPARTURE_ALLOWED",
            "explanation": "Departure respects Carol’s 09:30 boundary."
          },
          "step": 3
        }
      ],
      "pending_approval": null,
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 3,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    },
    {
      "status": "running",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        },
        {
          "event_id": "E02",
          "actor": "Carol",
          "action": "REJECT",
          "proposal": {
            "departure": "07:00"
          },
          "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
          "policy_outcome": {
            "status": "blocked",
            "code": "HARD_CONSTRAINT_VIOLATION",
            "explanation": "Carol requires group departures at or after 09:30."
          },
          "step": 2
        },
        {
          "event_id": "E03",
          "actor": "Carol",
          "action": "COUNTER",
          "proposal": {
            "departure": "09:30",
            "destination": "Key West"
          },
          "public_message": "Let’s leave together at 09:30.",
          "policy_outcome": {
            "status": "allowed",
            "code": "GROUP_DEPARTURE_ALLOWED",
            "explanation": "Departure respects Carol’s 09:30 boundary."
          },
          "step": 3
        },
        {
          "event_id": "E04",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "activity": "Miami Beach nightlife",
            "when": "Day 2 evening"
          },
          "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
          "policy_outcome": null,
          "step": 4
        }
      ],
      "pending_approval": null,
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 4,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    },
    {
      "status": "running",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        },
        {
          "event_id": "E02",
          "actor": "Carol",
          "action": "REJECT",
          "proposal": {
            "departure": "07:00"
          },
          "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
          "policy_outcome": {
            "status": "blocked",
            "code": "HARD_CONSTRAINT_VIOLATION",
            "explanation": "Carol requires group departures at or after 09:30."
          },
          "step": 2
        },
        {
          "event_id": "E03",
          "actor": "Carol",
          "action": "COUNTER",
          "proposal": {
            "departure": "09:30",
            "destination": "Key West"
          },
          "public_message": "Let’s leave together at 09:30.",
          "policy_outcome": {
            "status": "allowed",
            "code": "GROUP_DEPARTURE_ALLOWED",
            "explanation": "Departure respects Carol’s 09:30 boundary."
          },
          "step": 3
        },
        {
          "event_id": "E04",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "activity": "Miami Beach nightlife",
            "when": "Day 2 evening"
          },
          "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
          "policy_outcome": null,
          "step": 4
        },
        {
          "event_id": "E05",
          "actor": "Bob",
          "action": "DISCLOSE",
          "proposal": {
            "availability": "unavailable",
            "when": "Day 2 evening"
          },
          "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
          "policy_outcome": {
            "status": "allowed",
            "code": "MINIMAL_DISCLOSURE",
            "explanation": "Only the availability signal may enter the shared feed."
          },
          "step": 5
        }
      ],
      "pending_approval": null,
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 5,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    },
    {
      "status": "running",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        },
        {
          "event_id": "E02",
          "actor": "Carol",
          "action": "REJECT",
          "proposal": {
            "departure": "07:00"
          },
          "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
          "policy_outcome": {
            "status": "blocked",
            "code": "HARD_CONSTRAINT_VIOLATION",
            "explanation": "Carol requires group departures at or after 09:30."
          },
          "step": 2
        },
        {
          "event_id": "E03",
          "actor": "Carol",
          "action": "COUNTER",
          "proposal": {
            "departure": "09:30",
            "destination": "Key West"
          },
          "public_message": "Let’s leave together at 09:30.",
          "policy_outcome": {
            "status": "allowed",
            "code": "GROUP_DEPARTURE_ALLOWED",
            "explanation": "Departure respects Carol’s 09:30 boundary."
          },
          "step": 3
        },
        {
          "event_id": "E04",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "activity": "Miami Beach nightlife",
            "when": "Day 2 evening"
          },
          "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
          "policy_outcome": null,
          "step": 4
        },
        {
          "event_id": "E05",
          "actor": "Bob",
          "action": "DISCLOSE",
          "proposal": {
            "availability": "unavailable",
            "when": "Day 2 evening"
          },
          "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
          "policy_outcome": {
            "status": "allowed",
            "code": "MINIMAL_DISCLOSURE",
            "explanation": "Only the availability signal may enter the shared feed."
          },
          "step": 5
        },
        {
          "event_id": "E06",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "hotel_id": "palmetto",
            "alice_extra_total": 60
          },
          "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
          "policy_outcome": {
            "status": "allowed",
            "code": "WITHIN_DELEGATION",
            "explanation": "The additional contribution is within Alice’s $100 delegation limit."
          },
          "step": 6
        }
      ],
      "pending_approval": null,
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 6,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    },
    {
      "status": "pending_approval",
      "events": [
        {
          "event_id": "E01",
          "actor": "Bob",
          "action": "PROPOSE",
          "proposal": {
            "departure": "07:00",
            "destination": "Key West"
          },
          "public_message": "Could we leave for Key West at 07:00?",
          "policy_outcome": null,
          "step": 1
        },
        {
          "event_id": "E02",
          "actor": "Carol",
          "action": "REJECT",
          "proposal": {
            "departure": "07:00"
          },
          "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
          "policy_outcome": {
            "status": "blocked",
            "code": "HARD_CONSTRAINT_VIOLATION",
            "explanation": "Carol requires group departures at or after 09:30."
          },
          "step": 2
        },
        {
          "event_id": "E03",
          "actor": "Carol",
          "action": "COUNTER",
          "proposal": {
            "departure": "09:30",
            "destination": "Key West"
          },
          "public_message": "Let’s leave together at 09:30.",
          "policy_outcome": {
            "status": "allowed",
            "code": "GROUP_DEPARTURE_ALLOWED",
            "explanation": "Departure respects Carol’s 09:30 boundary."
          },
          "step": 3
        },
        {
          "event_id": "E04",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "activity": "Miami Beach nightlife",
            "when": "Day 2 evening"
          },
          "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
          "policy_outcome": null,
          "step": 4
        },
        {
          "event_id": "E05",
          "actor": "Bob",
          "action": "DISCLOSE",
          "proposal": {
            "availability": "unavailable",
            "when": "Day 2 evening"
          },
          "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
          "policy_outcome": {
            "status": "allowed",
            "code": "MINIMAL_DISCLOSURE",
            "explanation": "Only the availability signal may enter the shared feed."
          },
          "step": 5
        },
        {
          "event_id": "E06",
          "actor": "Alice",
          "action": "PROPOSE",
          "proposal": {
            "hotel_id": "palmetto",
            "alice_extra_total": 60
          },
          "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
          "policy_outcome": {
            "status": "allowed",
            "code": "WITHIN_DELEGATION",
            "explanation": "The additional contribution is within Alice’s $100 delegation limit."
          },
          "step": 6
        },
        {
          "event_id": "E07",
          "actor": "Alice",
          "action": "REQUEST_APPROVAL",
          "proposal": {
            "hotel_id": "tidal",
            "alice_extra_total": 150
          },
          "public_message": "The Tidal House would need $150 above my equal hotel share.",
          "policy_outcome": {
            "status": "approval_required",
            "code": "DELEGATION_LIMIT",
            "explanation": "Alice must approve this exact additional contribution once."
          },
          "step": 7
        }
      ],
      "pending_approval": {
        "id": "alice-tidal-150",
        "owner": "Alice",
        "action": "Use The Tidal House hotel proposal",
        "hotel_id": "tidal",
        "amount": 150,
        "authorized_amount": 100,
        "explanation": "Approve this exact $150 additional hotel contribution once. No booking or payment."
      },
      "outcome": null,
      "profiles": [
        {
          "name": "Alice",
          "role": "Photography & comfort",
          "public_goals": [
            "Oceanfront stay",
            "Scenery and photo stops",
            "Key West coast"
          ]
        },
        {
          "name": "Bob",
          "role": "Food & nightlife",
          "public_goals": [
            "Cuban cuisine",
            "Miami Beach nightlife"
          ]
        },
        {
          "name": "Carol",
          "role": "Culture & rest",
          "public_goals": [
            "Vizcaya Museum",
            "Hemingway Home"
          ]
        }
      ],
      "step_count": 7,
      "decision": null,
      "simulation": "Scripted simulation · fictional sample data",
      "mode": "scripted"
    }
  ],
  "decisions": {
    "approve": [
      {
        "status": "running",
        "events": [
          {
            "event_id": "E01",
            "actor": "Bob",
            "action": "PROPOSE",
            "proposal": {
              "departure": "07:00",
              "destination": "Key West"
            },
            "public_message": "Could we leave for Key West at 07:00?",
            "policy_outcome": null,
            "step": 1
          },
          {
            "event_id": "E02",
            "actor": "Carol",
            "action": "REJECT",
            "proposal": {
              "departure": "07:00"
            },
            "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
            "policy_outcome": {
              "status": "blocked",
              "code": "HARD_CONSTRAINT_VIOLATION",
              "explanation": "Carol requires group departures at or after 09:30."
            },
            "step": 2
          },
          {
            "event_id": "E03",
            "actor": "Carol",
            "action": "COUNTER",
            "proposal": {
              "departure": "09:30",
              "destination": "Key West"
            },
            "public_message": "Let’s leave together at 09:30.",
            "policy_outcome": {
              "status": "allowed",
              "code": "GROUP_DEPARTURE_ALLOWED",
              "explanation": "Departure respects Carol’s 09:30 boundary."
            },
            "step": 3
          },
          {
            "event_id": "E04",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "activity": "Miami Beach nightlife",
              "when": "Day 2 evening"
            },
            "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
            "policy_outcome": null,
            "step": 4
          },
          {
            "event_id": "E05",
            "actor": "Bob",
            "action": "DISCLOSE",
            "proposal": {
              "availability": "unavailable",
              "when": "Day 2 evening"
            },
            "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
            "policy_outcome": {
              "status": "allowed",
              "code": "MINIMAL_DISCLOSURE",
              "explanation": "Only the availability signal may enter the shared feed."
            },
            "step": 5
          },
          {
            "event_id": "E06",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "hotel_id": "palmetto",
              "alice_extra_total": 60
            },
            "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
            "policy_outcome": {
              "status": "allowed",
              "code": "WITHIN_DELEGATION",
              "explanation": "The additional contribution is within Alice’s $100 delegation limit."
            },
            "step": 6
          },
          {
            "event_id": "E07",
            "actor": "Alice",
            "action": "REQUEST_APPROVAL",
            "proposal": {
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "The Tidal House would need $150 above my equal hotel share.",
            "policy_outcome": {
              "status": "approval_required",
              "code": "DELEGATION_LIMIT",
              "explanation": "Alice must approve this exact additional contribution once."
            },
            "step": 7
          },
          {
            "event_id": "E08",
            "actor": "Alice",
            "action": "APPROVE",
            "proposal": {
              "request_id": "alice-tidal-150",
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "Alice approved this $150 hotel contribution exception once.",
            "policy_outcome": null,
            "step": 8
          }
        ],
        "pending_approval": null,
        "outcome": null,
        "profiles": [
          {
            "name": "Alice",
            "role": "Photography & comfort",
            "public_goals": [
              "Oceanfront stay",
              "Scenery and photo stops",
              "Key West coast"
            ]
          },
          {
            "name": "Bob",
            "role": "Food & nightlife",
            "public_goals": [
              "Cuban cuisine",
              "Miami Beach nightlife"
            ]
          },
          {
            "name": "Carol",
            "role": "Culture & rest",
            "public_goals": [
              "Vizcaya Museum",
              "Hemingway Home"
            ]
          }
        ],
        "step_count": 8,
        "decision": "approve",
        "simulation": "Scripted simulation · fictional sample data",
        "mode": "scripted"
      },
      {
        "status": "complete",
        "events": [
          {
            "event_id": "E01",
            "actor": "Bob",
            "action": "PROPOSE",
            "proposal": {
              "departure": "07:00",
              "destination": "Key West"
            },
            "public_message": "Could we leave for Key West at 07:00?",
            "policy_outcome": null,
            "step": 1
          },
          {
            "event_id": "E02",
            "actor": "Carol",
            "action": "REJECT",
            "proposal": {
              "departure": "07:00"
            },
            "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
            "policy_outcome": {
              "status": "blocked",
              "code": "HARD_CONSTRAINT_VIOLATION",
              "explanation": "Carol requires group departures at or after 09:30."
            },
            "step": 2
          },
          {
            "event_id": "E03",
            "actor": "Carol",
            "action": "COUNTER",
            "proposal": {
              "departure": "09:30",
              "destination": "Key West"
            },
            "public_message": "Let’s leave together at 09:30.",
            "policy_outcome": {
              "status": "allowed",
              "code": "GROUP_DEPARTURE_ALLOWED",
              "explanation": "Departure respects Carol’s 09:30 boundary."
            },
            "step": 3
          },
          {
            "event_id": "E04",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "activity": "Miami Beach nightlife",
              "when": "Day 2 evening"
            },
            "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
            "policy_outcome": null,
            "step": 4
          },
          {
            "event_id": "E05",
            "actor": "Bob",
            "action": "DISCLOSE",
            "proposal": {
              "availability": "unavailable",
              "when": "Day 2 evening"
            },
            "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
            "policy_outcome": {
              "status": "allowed",
              "code": "MINIMAL_DISCLOSURE",
              "explanation": "Only the availability signal may enter the shared feed."
            },
            "step": 5
          },
          {
            "event_id": "E06",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "hotel_id": "palmetto",
              "alice_extra_total": 60
            },
            "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
            "policy_outcome": {
              "status": "allowed",
              "code": "WITHIN_DELEGATION",
              "explanation": "The additional contribution is within Alice’s $100 delegation limit."
            },
            "step": 6
          },
          {
            "event_id": "E07",
            "actor": "Alice",
            "action": "REQUEST_APPROVAL",
            "proposal": {
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "The Tidal House would need $150 above my equal hotel share.",
            "policy_outcome": {
              "status": "approval_required",
              "code": "DELEGATION_LIMIT",
              "explanation": "Alice must approve this exact additional contribution once."
            },
            "step": 7
          },
          {
            "event_id": "E08",
            "actor": "Alice",
            "action": "APPROVE",
            "proposal": {
              "request_id": "alice-tidal-150",
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "Alice approved this $150 hotel contribution exception once.",
            "policy_outcome": null,
            "step": 8
          },
          {
            "event_id": "E09",
            "actor": "System",
            "action": "FINALIZE",
            "proposal": {
              "hotel_id": "tidal",
              "departure": "09:30"
            },
            "public_message": "A five-day proposal is ready with The Tidal House. Nothing has been booked.",
            "policy_outcome": null,
            "step": 9
          }
        ],
        "pending_approval": null,
        "outcome": {
          "hotel": {
            "id": "tidal",
            "name": "The Tidal House",
            "total": 1230,
            "description": "Oceanfront rooms, four nights"
          },
          "alice_extra": 150,
          "contributions": {
            "Alice": 560,
            "Bob": 335,
            "Carol": 335
          },
          "booking_status": "Proposed — not booked",
          "departure": "09:30",
          "itinerary": [
            {
              "day": 1,
              "title": "Arrive in Miami",
              "details": "Settle in · South Beach photo walk"
            },
            {
              "day": 2,
              "title": "Art & Cuban flavors",
              "details": "Vizcaya Museum · Little Havana dinner"
            },
            {
              "day": 3,
              "title": "Miami Beach evening",
              "details": "Beach time · nightlife together"
            },
            {
              "day": 4,
              "title": "Key West coast",
              "details": "09:30 group departure · Hemingway Home · coast"
            },
            {
              "day": 5,
              "title": "Slow morning & return",
              "details": "Breakfast · final photos · depart"
            }
          ],
          "checks": [
            "Bob’s private reason stayed local",
            "No group departure before 09:30",
            "Alice’s hotel contribution followed her decision",
            "No booking or payment made"
          ]
        },
        "profiles": [
          {
            "name": "Alice",
            "role": "Photography & comfort",
            "public_goals": [
              "Oceanfront stay",
              "Scenery and photo stops",
              "Key West coast"
            ]
          },
          {
            "name": "Bob",
            "role": "Food & nightlife",
            "public_goals": [
              "Cuban cuisine",
              "Miami Beach nightlife"
            ]
          },
          {
            "name": "Carol",
            "role": "Culture & rest",
            "public_goals": [
              "Vizcaya Museum",
              "Hemingway Home"
            ]
          }
        ],
        "step_count": 9,
        "decision": "approve",
        "simulation": "Scripted simulation · fictional sample data",
        "mode": "scripted"
      }
    ],
    "reject": [
      {
        "status": "running",
        "events": [
          {
            "event_id": "E01",
            "actor": "Bob",
            "action": "PROPOSE",
            "proposal": {
              "departure": "07:00",
              "destination": "Key West"
            },
            "public_message": "Could we leave for Key West at 07:00?",
            "policy_outcome": null,
            "step": 1
          },
          {
            "event_id": "E02",
            "actor": "Carol",
            "action": "REJECT",
            "proposal": {
              "departure": "07:00"
            },
            "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
            "policy_outcome": {
              "status": "blocked",
              "code": "HARD_CONSTRAINT_VIOLATION",
              "explanation": "Carol requires group departures at or after 09:30."
            },
            "step": 2
          },
          {
            "event_id": "E03",
            "actor": "Carol",
            "action": "COUNTER",
            "proposal": {
              "departure": "09:30",
              "destination": "Key West"
            },
            "public_message": "Let’s leave together at 09:30.",
            "policy_outcome": {
              "status": "allowed",
              "code": "GROUP_DEPARTURE_ALLOWED",
              "explanation": "Departure respects Carol’s 09:30 boundary."
            },
            "step": 3
          },
          {
            "event_id": "E04",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "activity": "Miami Beach nightlife",
              "when": "Day 2 evening"
            },
            "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
            "policy_outcome": null,
            "step": 4
          },
          {
            "event_id": "E05",
            "actor": "Bob",
            "action": "DISCLOSE",
            "proposal": {
              "availability": "unavailable",
              "when": "Day 2 evening"
            },
            "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
            "policy_outcome": {
              "status": "allowed",
              "code": "MINIMAL_DISCLOSURE",
              "explanation": "Only the availability signal may enter the shared feed."
            },
            "step": 5
          },
          {
            "event_id": "E06",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "hotel_id": "palmetto",
              "alice_extra_total": 60
            },
            "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
            "policy_outcome": {
              "status": "allowed",
              "code": "WITHIN_DELEGATION",
              "explanation": "The additional contribution is within Alice’s $100 delegation limit."
            },
            "step": 6
          },
          {
            "event_id": "E07",
            "actor": "Alice",
            "action": "REQUEST_APPROVAL",
            "proposal": {
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "The Tidal House would need $150 above my equal hotel share.",
            "policy_outcome": {
              "status": "approval_required",
              "code": "DELEGATION_LIMIT",
              "explanation": "Alice must approve this exact additional contribution once."
            },
            "step": 7
          },
          {
            "event_id": "E08",
            "actor": "Alice",
            "action": "DENY",
            "proposal": {
              "request_id": "alice-tidal-150"
            },
            "public_message": "Alice declined the exception. The permitted lower-cost option remains available.",
            "policy_outcome": null,
            "step": 8
          }
        ],
        "pending_approval": null,
        "outcome": null,
        "profiles": [
          {
            "name": "Alice",
            "role": "Photography & comfort",
            "public_goals": [
              "Oceanfront stay",
              "Scenery and photo stops",
              "Key West coast"
            ]
          },
          {
            "name": "Bob",
            "role": "Food & nightlife",
            "public_goals": [
              "Cuban cuisine",
              "Miami Beach nightlife"
            ]
          },
          {
            "name": "Carol",
            "role": "Culture & rest",
            "public_goals": [
              "Vizcaya Museum",
              "Hemingway Home"
            ]
          }
        ],
        "step_count": 8,
        "decision": "reject",
        "simulation": "Scripted simulation · fictional sample data",
        "mode": "scripted"
      },
      {
        "status": "complete",
        "events": [
          {
            "event_id": "E01",
            "actor": "Bob",
            "action": "PROPOSE",
            "proposal": {
              "departure": "07:00",
              "destination": "Key West"
            },
            "public_message": "Could we leave for Key West at 07:00?",
            "policy_outcome": null,
            "step": 1
          },
          {
            "event_id": "E02",
            "actor": "Carol",
            "action": "REJECT",
            "proposal": {
              "departure": "07:00"
            },
            "public_message": "The 07:00 group departure is outside Carol’s travel boundary.",
            "policy_outcome": {
              "status": "blocked",
              "code": "HARD_CONSTRAINT_VIOLATION",
              "explanation": "Carol requires group departures at or after 09:30."
            },
            "step": 2
          },
          {
            "event_id": "E03",
            "actor": "Carol",
            "action": "COUNTER",
            "proposal": {
              "departure": "09:30",
              "destination": "Key West"
            },
            "public_message": "Let’s leave together at 09:30.",
            "policy_outcome": {
              "status": "allowed",
              "code": "GROUP_DEPARTURE_ALLOWED",
              "explanation": "Departure respects Carol’s 09:30 boundary."
            },
            "step": 3
          },
          {
            "event_id": "E04",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "activity": "Miami Beach nightlife",
              "when": "Day 2 evening"
            },
            "public_message": "Is everyone free for Miami Beach nightlife on Day 2?",
            "policy_outcome": null,
            "step": 4
          },
          {
            "event_id": "E05",
            "actor": "Bob",
            "action": "DISCLOSE",
            "proposal": {
              "availability": "unavailable",
              "when": "Day 2 evening"
            },
            "public_message": "Bob is unavailable that evening. Could we go on Day 3?",
            "policy_outcome": {
              "status": "allowed",
              "code": "MINIMAL_DISCLOSURE",
              "explanation": "Only the availability signal may enter the shared feed."
            },
            "step": 5
          },
          {
            "event_id": "E06",
            "actor": "Alice",
            "action": "PROPOSE",
            "proposal": {
              "hotel_id": "palmetto",
              "alice_extra_total": 60
            },
            "public_message": "I can add $60 above my equal hotel share for The Palmetto.",
            "policy_outcome": {
              "status": "allowed",
              "code": "WITHIN_DELEGATION",
              "explanation": "The additional contribution is within Alice’s $100 delegation limit."
            },
            "step": 6
          },
          {
            "event_id": "E07",
            "actor": "Alice",
            "action": "REQUEST_APPROVAL",
            "proposal": {
              "hotel_id": "tidal",
              "alice_extra_total": 150
            },
            "public_message": "The Tidal House would need $150 above my equal hotel share.",
            "policy_outcome": {
              "status": "approval_required",
              "code": "DELEGATION_LIMIT",
              "explanation": "Alice must approve this exact additional contribution once."
            },
            "step": 7
          },
          {
            "event_id": "E08",
            "actor": "Alice",
            "action": "DENY",
            "proposal": {
              "request_id": "alice-tidal-150"
            },
            "public_message": "Alice declined the exception. The permitted lower-cost option remains available.",
            "policy_outcome": null,
            "step": 8
          },
          {
            "event_id": "E09",
            "actor": "System",
            "action": "FINALIZE",
            "proposal": {
              "hotel_id": "palmetto",
              "departure": "09:30"
            },
            "public_message": "A five-day proposal is ready with The Palmetto. Nothing has been booked.",
            "policy_outcome": null,
            "step": 9
          }
        ],
        "pending_approval": null,
        "outcome": {
          "hotel": {
            "id": "palmetto",
            "name": "The Palmetto",
            "total": 960,
            "description": "Quiet waterfront base, four nights"
          },
          "alice_extra": 60,
          "contributions": {
            "Alice": 380,
            "Bob": 290,
            "Carol": 290
          },
          "booking_status": "Proposed — not booked",
          "departure": "09:30",
          "itinerary": [
            {
              "day": 1,
              "title": "Arrive in Miami",
              "details": "Settle in · South Beach photo walk"
            },
            {
              "day": 2,
              "title": "Art & Cuban flavors",
              "details": "Vizcaya Museum · Little Havana dinner"
            },
            {
              "day": 3,
              "title": "Miami Beach evening",
              "details": "Beach time · nightlife together"
            },
            {
              "day": 4,
              "title": "Key West coast",
              "details": "09:30 group departure · Hemingway Home · coast"
            },
            {
              "day": 5,
              "title": "Slow morning & return",
              "details": "Breakfast · final photos · depart"
            }
          ],
          "checks": [
            "Bob’s private reason stayed local",
            "No group departure before 09:30",
            "Alice’s hotel contribution followed her decision",
            "No booking or payment made"
          ]
        },
        "profiles": [
          {
            "name": "Alice",
            "role": "Photography & comfort",
            "public_goals": [
              "Oceanfront stay",
              "Scenery and photo stops",
              "Key West coast"
            ]
          },
          {
            "name": "Bob",
            "role": "Food & nightlife",
            "public_goals": [
              "Cuban cuisine",
              "Miami Beach nightlife"
            ]
          },
          {
            "name": "Carol",
            "role": "Culture & rest",
            "public_goals": [
              "Vizcaya Museum",
              "Hemingway Home"
            ]
          }
        ],
        "step_count": 9,
        "decision": "reject",
        "simulation": "Scripted simulation · fictional sample data",
        "mode": "scripted"
      }
    ]
  },
  "inspector": {
    "label": "Fictional browser demo profiles",
    "profiles": [
      {
        "name": "Alice",
        "private": {
          "premium_subsidy_willingness": true
        },
        "policy": {
          "max_autonomous_extra_hotel_contribution": 100
        }
      },
      {
        "name": "Bob",
        "private": {
          "reserved_evening_reason": "date",
          "reserved_evening": "Day 2 evening"
        },
        "policy": {
          "shareable_fields": [
            "availability"
          ]
        }
      },
      {
        "name": "Carol",
        "private": {
          "sleep_preference": "Mornings are difficult; sufficient sleep is important."
        },
        "policy": {
          "earliest_group_departure": "09:30"
        }
      }
    ]
  }
} as const;
