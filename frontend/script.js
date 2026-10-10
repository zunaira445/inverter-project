const grid = document.getElementById("productGrid");
const count = document.getElementById("resultCount");
const searchInput = document.getElementById("searchInput");
const brandFilter = document.getElementById("brandFilter");
const searchButton = document.getElementById("searchButton");
const dialog = document.getElementById("detailsDialog");
const detailsContent = document.getElementById("detailsContent");

let allProducts = [];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function formatPrice(value) {
    if (value === null || value === undefined || value === "") {
        return "Price unavailable";
    }
    return "Rs. " + Number(value).toLocaleString("en-PK", {
        maximumFractionDigits: 2
    });
}

function productCard(p) {
    const image = p.image_url
        ? `<img class="product-image" src="${escapeHTML(p.image_url)}"
                alt="${escapeHTML(p.product_name)}"
                loading="lazy"
                onerror="this.style.display='none';this.nextElementSibling.style.display='block'">`
        : "";

    return `
        <article class="product-card">
            <div class="image-wrap">
                ${image}
                <span class="image-placeholder"
                      style="display:${p.image_url ? "none" : "block"}">
                    Image unavailable
                </span>
            </div>
            <div class="card-body">
                <span class="brand">${escapeHTML(p.brand || "Solar inverter")}</span>
                <h3 class="product-name">${escapeHTML(p.product_name)}</h3>
                <p class="model">Model: ${escapeHTML(p.model || "Not specified")}</p>
                <div class="price-row">
                    <span class="price">${formatPrice(p.current_price)}</span>
                    ${p.original_price && p.original_price > (p.current_price || 0)
                        ? `<span class="old-price">${formatPrice(p.original_price)}</span>`
                        : ""}
                </div>
                <p class="product-description">${escapeHTML((p.description || "").slice(0, 170))}${(p.description || "").length > 170 ? "..." : ""}</p>
                <button class="details-button" data-id="${p.id}">View Details</button>
            </div>
        </article>`;
}

function renderProducts(products) {
    count.textContent = `${products.length} product${products.length === 1 ? "" : "s"} found`;

    if (!products.length) {
        grid.innerHTML = '<p class="message">No products found. Try another search.</p>';
        return;
    }

    grid.innerHTML = products.map(productCard).join("");
}

async function loadProducts() {
    grid.innerHTML = '<p class="message">Loading products from database...</p>';

    try {
        const response = await fetch("/api/inverters");
        if (!response.ok) throw new Error("API request failed");

        const data = await response.json();
        allProducts = data.products;

        const brands = [...new Set(allProducts.map(p => p.brand).filter(Boolean))]
            .sort((a, b) => a.localeCompare(b));

        brandFilter.innerHTML = '<option value="">All brands</option>' +
            brands.map(brand =>
                `<option value="${escapeHTML(brand)}">${escapeHTML(brand)}</option>`
            ).join("");

        renderProducts(allProducts);
    } catch (error) {
        count.textContent = "Unable to load products";
        grid.innerHTML = '<p class="message">Backend se connection nahi ho saka. Server check karo aur page refresh karo.</p>';
        console.error(error);
    }
}

async function searchProducts() {
    const q = searchInput.value.trim();
    const brand = brandFilter.value;
    const params = new URLSearchParams();

    if (q) params.set("q", q);
    if (brand) params.set("brand", brand);

    grid.innerHTML = '<p class="message">Searching...</p>';

    try {
        const response = await fetch("/api/inverters?" + params.toString());
        if (!response.ok) throw new Error("Search request failed");
        const data = await response.json();
        renderProducts(data.products);
    } catch (error) {
        grid.innerHTML = '<p class="message">Search nahi ho saki. Backend check karo.</p>';
        console.error(error);
    }
}

searchButton.addEventListener("click", searchProducts);
brandFilter.addEventListener("change", searchProducts);
searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") searchProducts();
});

grid.addEventListener("click", event => {
    const button = event.target.closest("[data-id]");
    if (!button) return;

    const product = allProducts.find(p => p.id === Number(button.dataset.id));
    if (!product) {
        fetch("/api/inverters/" + button.dataset.id)
            .then(response => response.json())
            .then(showDetails)
            .catch(console.error);
        return;
    }
    showDetails(product);
});

function showDetails(p) {
    detailsContent.innerHTML = `
        <span class="brand">${escapeHTML(p.brand)}</span>
        <h2>${escapeHTML(p.product_name)}</h2>
        <p class="model">Model: ${escapeHTML(p.model || "Not specified")}</p>
        ${p.image_url
            ? `<img class="details-image" src="${escapeHTML(p.image_url)}" alt="${escapeHTML(p.product_name)}">`
            : ""}
        <h3>${formatPrice(p.current_price)}</h3>
        <p>Original price: ${formatPrice(p.original_price)}</p>
        <h3>Specifications and description</h3>
        <p class="details-text">${escapeHTML(p.description || "No description available.")}</p>
        <p><a href="${escapeHTML(p.product_url)}" target="_blank" rel="noopener noreferrer">View original product page</a></p>
    `;
    dialog.showModal();
}

document.getElementById("closeDialog").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
});

loadProducts();
