document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    Brand: document.getElementById('Brand').value,
    body_type: document.getElementById('body_type').value,
    fuel_type: document.getElementById('fuel_type').value,
    transmission_type: document.getElementById('transmission_type').value,
    owner_type: document.getElementById('owner_type').value,
    insurance: document.getElementById('insurance').value,
    city: document.getElementById('city').value,
    Year: document.getElementById('Year').value,
    registered_year: document.getElementById('registered_year').value,
    driven: document.getElementById('driven').value,
    max_power: document.getElementById('max_power').value,
    engine_size: document.getElementById('engine_size').value,
    seats: document.getElementById('seats').value,
    avg: document.getElementById('avg').value,
  };

  const resultBox = document.getElementById('resultBox');
  const resultText = document.getElementById('resultText');

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    resultBox.classList.remove('hidden', 'error');

    if (data.success) {
      resultText.textContent = `Estimated Price: ₹${data.predicted_price.toLocaleString('en-IN')}`;
    } else {
      resultBox.classList.add('error');
      resultText.textContent = `Error: ${data.error}`;
    }
  } catch (err) {
    resultBox.classList.remove('hidden');
    resultBox.classList.add('error');
    resultText.textContent = `Request failed: ${err.message}`;
  }
});
