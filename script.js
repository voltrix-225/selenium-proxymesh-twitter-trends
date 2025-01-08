document.getElementById('run-script-btn').addEventListener('click', async () => {
    const response = await fetch('/run-script', { method: 'POST' });
    const data = await response.json();

    const resultDiv = document.getElementById('result');
    if (data.error) {
        resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
    } else {
        resultDiv.innerHTML = `
            <p>These are the most happening topics as on ${data.timestamp}</p>
            <ul>
                <li>${data.trend1}</li>
                <li>${data.trend2}</li>
                <li>${data.trend3}</li>
                <li>${data.trend4}</li>
                <li>${data.trend5}</li>
            </ul>
            <p>The IP address used for this query was ${data.ip_address}.</p>
            <p>Here’s a JSON extract of this record from MongoDB:</p>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
    }
});
