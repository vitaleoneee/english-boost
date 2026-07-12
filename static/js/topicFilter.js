function updateTopicFilterLabel(filter) {
    const button = filter.querySelector(".topic-filter-toggle");
    const label = filter.querySelector(".topic-filter-label");
    const selected = filter.querySelectorAll('input[name="topic"]:checked');

    if (!selected.length) {
        label.textContent = button.dataset.allLabel;
    } else if (selected.length === 1) {
        label.textContent = selected[0].dataset.topicName;
    } else {
        label.textContent = `${button.dataset.selectedLabel}: ${selected.length}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".topic-filter").forEach(updateTopicFilterLabel);
});

document.addEventListener("change", (event) => {
    if (!event.target.matches('.topic-filter input[name="topic"]')) {
        return;
    }

    updateTopicFilterLabel(event.target.closest(".topic-filter"));
});
