document.addEventListener('DOMContentLoaded', () => {
  const eventsContainer = document.getElementById('events-container');

  // Fetch the real scraped JSON events
  fetch('./real_entries/events.json')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      renderEvents(data);
    })
    .catch(error => {
      console.error('Error loading events:', error);
      eventsContainer.innerHTML = `<div class="loading-state"><p>Error loading jazz events. Please try again later.</p></div>`;
    });

  function renderEvents(events) {
    if (!events || events.length === 0) {
      eventsContainer.innerHTML = `<div class="loading-state"><p>No upcoming events found.</p></div>`;
      return;
    }

    eventsContainer.innerHTML = '';

    // Group events by date
    const groupedEvents = events.reduce((acc, event) => {
      if (!acc[event.date]) {
        acc[event.date] = [];
      }
      acc[event.date].push(event);
      return acc;
    }, {});

    // Sort dates
    const sortedDates = Object.keys(groupedEvents).sort();

    // Formatting date
    const formatDate = (dateStr) => {
      const options = { weekday: 'long', month: 'long', day: 'numeric' };
      // Parse date with time to avoid timezone shift issues initially
      const date = new Date(`${dateStr}T12:00:00`); 
      return date.toLocaleDateString('en-US', options);
    };

    sortedDates.forEach(date => {
      const groupEl = document.createElement('div');
      groupEl.className = 'date-group';

      const headerEl = document.createElement('h2');
      headerEl.className = 'date-header';
      headerEl.textContent = formatDate(date);
      groupEl.appendChild(headerEl);

      groupedEvents[date].forEach(event => {
        const personnelText = event.personnel.map(p => `<span>${p.name}</span> (${p.instrument})`).join(', ');

        const cardEl = document.createElement('div');
        cardEl.className = 'event-card';
        cardEl.innerHTML = `
          <div class="event-time">${event.time}</div>
          <div class="event-details">
            <h3>${event.artist}</h3>
            <div class="event-venue">
              <span class="venue-name">${event.venue.name}</span> — ${event.venue.address}
            </div>
            <div class="event-personnel">
              ${personnelText}
            </div>
            <div class="event-footer">
              <span class="ticket-price">${event.priceRange}</span>
              <a href="${event.ticketLink}" class="ticket-link">Tickets</a>
              <a href="#" class="more-events">More events</a>
            </div>
          </div>
        `;
        groupEl.appendChild(cardEl);
      });

      eventsContainer.appendChild(groupEl);
    });
  }
});
