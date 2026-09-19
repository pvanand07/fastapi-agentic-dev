async function loadExamples() {
  const res = await fetch("/api/examples/");
  const items = await res.json();
  const list = document.getElementById("examples");
  list.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item.name;
    list.appendChild(li);
  }
}

loadExamples();
