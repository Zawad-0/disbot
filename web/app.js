const state = {
  devices: [],
  summary: null,
  alerts: [],
};

const roomOrder = ["drawing", "work1", "work2"];

async function fetchJson(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

function groupByRoom(devices) {
  return devices.reduce((rooms, device) => {
    rooms[device.room_id] ||= {
      roomName: device.room_name,
      devices: [],
    };
    rooms[device.room_id].devices.push(device);
    return rooms;
  }, {});
}

function renderSummary() {
  if (!state.summary) return;
  document.getElementById("totalPower").textContent = `${state.summary.total_power_watts} W`;
  document.getElementById("dailyUsage").textContent = `${state.summary.estimated_daily_kwh} kWh/day`;
  document.getElementById("updatedAt").textContent = `Updated ${new Date(state.summary.generated_at).toLocaleTimeString()}`;
}

function renderOfficeLayout() {
  const rooms = groupByRoom(state.devices);
  const root = document.getElementById("officeLayout");
  root.innerHTML = roomOrder
    .map((roomId) => {
      const room = rooms[roomId];
      const roomSummary = state.summary.rooms[roomId];
      const fixtures = room.devices
        .map((device) => {
          const label = device.type === "fan" ? "F" : "L";
          return `<div class="fixture is-${device.type} ${device.status ? "is-on" : ""}" title="${device.name}">${label}</div>`;
        })
        .join("");
      return `
        <article class="room-map ${roomSummary.on_count ? "is-active" : ""}">
          <h2>${room.roomName}</h2>
          <div class="fixture-row">${fixtures}</div>
          <p class="room-meta">${roomSummary.on_count}/${roomSummary.device_count} on · ${roomSummary.power_watts} W</p>
        </article>
      `;
    })
    .join("");
}

function renderStatusGrid() {
  const rooms = groupByRoom(state.devices);
  const root = document.getElementById("statusGrid");
  root.innerHTML = roomOrder
    .map((roomId) => {
      const room = rooms[roomId];
      const roomSummary = state.summary.rooms[roomId];
      const devices = room.devices
        .map((device) => `
          <div class="device">
            <div>
              <div class="device-name">${device.name}</div>
              <div class="device-meta">${device.type} · ${device.current_power_watts} W · ${device.status_label}</div>
            </div>
            <button class="toggle ${device.status ? "is-on" : ""}" aria-label="Toggle ${device.name}" data-device-id="${device.id}"></button>
          </div>
        `)
        .join("");
      return `
        <article class="room-card">
          <header>
            <div>
              <h2>${room.roomName}</h2>
              <p class="room-meta">${roomSummary.fan_on_count} fans on · ${roomSummary.light_on_count} lights on</p>
            </div>
            <strong>${roomSummary.power_watts} W</strong>
          </header>
          <div class="device-list">${devices}</div>
        </article>
      `;
    })
    .join("");
}

function renderAlerts() {
  const root = document.getElementById("alertsList");
  if (!state.alerts.length) {
    root.innerHTML = '<div class="empty-alert">No active alerts.</div>';
    return;
  }

  root.innerHTML = state.alerts
    .map((alert) => `<div class="alert ${alert.severity}">${alert.message}</div>`)
    .join("");
}

function render() {
  renderSummary();
  renderOfficeLayout();
  renderStatusGrid();
  renderAlerts();
}

async function refresh() {
  const [devices, summary, alerts] = await Promise.all([
    fetchJson("/api/devices"),
    fetchJson("/api/summary"),
    fetchJson("/api/alerts"),
  ]);
  state.devices = devices;
  state.summary = summary;
  state.alerts = alerts;
  render();
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-device-id]");
  if (!button) return;
  button.disabled = true;
  await fetchJson(`/api/devices/${button.dataset.deviceId}/toggle`, { method: "POST" });
  await refresh();
});

refresh().catch((error) => {
  document.getElementById("updatedAt").textContent = error.message;
});

setInterval(() => refresh().catch(console.error), 2500);
