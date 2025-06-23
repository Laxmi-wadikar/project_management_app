async function loadDashboard() {
  const userId = document.getElementById("employee").value;
  const department = document.getElementById("department").value;
  const weekStart = document.getElementById("week_start").value;

  const url = new URL("/api/weekly_data", window.location.origin);
  if (userId) url.searchParams.append("user_id", userId);
  if (department) url.searchParams.append("department", department);
  if (weekStart) url.searchParams.append("week_start", weekStart);

  const res = await fetch(url);
  if (!res.ok) return alert("No data found");

  const data = await res.json();

  document.getElementById("client_closed").innerText = `Client Closed: ${data.client_closed}`;
  document.getElementById("cancellation").innerText = `Cancellation: ${data.cancellation}`;
  document.getElementById("magazine_published").innerText = `Magazines: ${data.magazine_published}`;
  document.getElementById("closer_amount").innerText = `Closer Amt: ₹${data.closer_amount}`;
  document.getElementById("payment_received").innerText = `Payment Rec: ₹${data.payment_received}`;
  document.getElementById("payable_amount").innerText = `Payable Amt: ₹${data.payable_amount}`;

  renderBarChart(data);
  renderPieChart(data);
}

let barChart, pieChart;

function renderBarChart(data) {
  const ctx = document.getElementById("barChart").getContext("2d");
  if (barChart) barChart.destroy();

  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Client Closed", "Cancellation", "Magazines"],
      datasets: [{
        label: "Weekly Summary",
        data: [data.client_closed, data.cancellation, data.magazine_published],
        backgroundColor: ["#00b894", "#d63031", "#6c5ce7"],
        borderRadius: 6
      }]
    }
  });
}

function renderPieChart(data) {
  const ctx = document.getElementById("pieChart").getContext("2d");
  if (pieChart) pieChart.destroy();

  pieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Closer Amount", "Payment Received", "Payable Amount"],
      datasets: [{
        data: [data.closer_amount, data.payment_received, data.payable_amount],
        backgroundColor: ["#0984e3", "#00cec9", "#fdcb6e"]
      }]
    }
  });
}

window.onload = loadDashboard;
