// Deal Finder: renders the deals, filters them, and routes between
// the list and one deal's page. No network: the data lives in
// deals.js, and every link out is an ordinary anchor to a store.

import { DEALS, CHECKED_ON, READ_AGAIN_ON } from "./deals.js";

const listView = document.getElementById("list");
const detailView = document.getElementById("detail");
const searchBox = document.getElementById("search");
const categoryBox = document.getElementById("category");
const storeBox = document.getElementById("store");
const discountBox = document.getElementById("discount");
const sortBox = document.getElementById("sort");
const countLine = document.getElementById("count");
const checkedLine = document.getElementById("checked");

function money(value) {
  return "$" + value.toFixed(2).replace(/\.00$/, "");
}

function discountOf(deal) {
  return Math.round((1 - deal.sale / deal.usual) * 100);
}

function savingOf(deal) {
  return deal.usual - deal.sale;
}

function signalClass(signal) {
  if (signal === "New low") return "signal newlow";
  if (signal === "Strong price") return "signal strong";
  if (signal === "Good price") return "signal good";
  return "signal modest";
}

function fillSelect(box, values) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    box.appendChild(option);
  }
}

function visibleDeals() {
  const query = searchBox.value.trim().toLowerCase();
  const category = categoryBox.value;
  const store = storeBox.value;
  const minimum = Number(discountBox.value);
  const sort = sortBox.value;
  let shown = DEALS.filter((deal) => {
    if (category !== "All" && deal.category !== category) return false;
    if (store !== "All" && deal.store !== store) return false;
    if (discountOf(deal) < minimum) return false;
    if (query) {
      const haystack = (deal.name + " " + deal.store + " " + deal.category).toLowerCase();
      if (!haystack.includes(query)) return false;
    }
    return true;
  });
  if (sort === "discount") shown.sort((a, b) => discountOf(b) - discountOf(a));
  if (sort === "saving") shown.sort((a, b) => savingOf(b) - savingOf(a));
  if (sort === "price") shown.sort((a, b) => a.sale - b.sale);
  if (sort === "name") shown.sort((a, b) => a.name.localeCompare(b.name));
  return shown;
}

function cardElement(deal) {
  const card = document.createElement("article");
  card.className = "card";
  const off = discountOf(deal);
  card.innerHTML = "";
  const title = document.createElement("h2");
  const link = document.createElement("a");
  link.href = "#/deal/" + deal.id;
  link.textContent = deal.name;
  title.appendChild(link);
  card.appendChild(title);

  const meta = document.createElement("p");
  meta.className = "meta";
  meta.textContent = deal.store + " · " + deal.category;
  card.appendChild(meta);

  const prices = document.createElement("p");
  prices.className = "prices";
  const sale = document.createElement("span");
  sale.className = "sale";
  sale.textContent = money(deal.sale);
  const usual = document.createElement("span");
  usual.className = "usual";
  usual.textContent = money(deal.usual);
  const badge = document.createElement("span");
  badge.className = "off";
  badge.textContent = "−" + off + "%";
  prices.append(sale, document.createTextNode(" "), usual, document.createTextNode(" "), badge);
  card.appendChild(prices);

  const signal = document.createElement("p");
  const chip = document.createElement("span");
  chip.className = signalClass(deal.signal);
  chip.textContent = deal.signal;
  signal.append(chip, document.createTextNode(" " + deal.note));
  card.appendChild(signal);

  const foot = document.createElement("p");
  foot.className = "foot";
  const storeLink = document.createElement("a");
  storeLink.href = deal.url;
  storeLink.rel = "noopener";
  storeLink.textContent = "View at " + deal.store;
  foot.appendChild(storeLink);
  foot.appendChild(document.createTextNode(" · Checked " + CHECKED_ON));
  card.appendChild(foot);
  return card;
}

function renderList() {
  detailView.hidden = true;
  listView.hidden = false;
  listView.replaceChildren();
  const shown = visibleDeals();
  for (const deal of shown) listView.appendChild(cardElement(deal));
  if (shown.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No deals match those filters. Clear the search or lower the minimum discount.";
    listView.appendChild(empty);
  }
  countLine.textContent =
    shown.length + " of " + DEALS.length + " deals · sorted by " + sortBox.selectedOptions[0].textContent;
}

function renderDetail(id) {
  const deal = DEALS.find((candidate) => candidate.id === id);
  listView.hidden = true;
  detailView.hidden = false;
  detailView.replaceChildren();
  if (!deal) {
    const missing = document.createElement("p");
    missing.textContent = "No deal with that name. ";
    const back = document.createElement("a");
    back.href = "#/";
    back.textContent = "Back to all deals";
    missing.appendChild(back);
    detailView.appendChild(missing);
    return;
  }
  const back = document.createElement("p");
  const backLink = document.createElement("a");
  backLink.href = "#/";
  backLink.textContent = "← All deals";
  back.appendChild(backLink);
  detailView.appendChild(back);
  detailView.appendChild(cardElement(deal));
  const source = document.createElement("p");
  source.className = "source";
  source.textContent = "Price source: " + deal.source + ". Checked " + CHECKED_ON + ", re-read " + READ_AGAIN_ON + ". Prices can change; check the store before you buy.";
  detailView.appendChild(source);
}

function route() {
  const hash = location.hash || "#/";
  if (hash.startsWith("#/deal/")) {
    renderDetail(hash.slice("#/deal/".length));
  } else {
    renderList();
  }
}

for (const box of [searchBox, categoryBox, storeBox, discountBox, sortBox]) {
  box.addEventListener("input", () => {
    if (!detailView.hidden) location.hash = "#/";
    renderList();
  });
}

fillSelect(categoryBox, ["All", ...new Set(DEALS.map((deal) => deal.category))]);
fillSelect(storeBox, ["All", ...new Set(DEALS.map((deal) => deal.store))]);
checkedLine.textContent =
  "Prices checked " + CHECKED_ON + ", re-read " + READ_AGAIN_ON + ". A deal is only listed when a store or a deals source that names the store showed the price.";
window.addEventListener("hashchange", route);
route();
