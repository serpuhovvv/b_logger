// ======================================================
//  Filters
// ======================================================

function initFilters() {
    const searchInput  = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const moduleFilter = document.getElementById('moduleFilter');
    const resetBtn     = document.getElementById("reset-filters");

    // --- события фильтров ---
    searchInput?.addEventListener('input', filterTests);
    statusFilter?.addEventListener('change', filterTests);
    moduleFilter?.addEventListener('change', filterTests);

    // Esc очищает поиск
    searchInput?.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            filterTests();
        }
    });

    // фильтр-кнопки
    document.querySelectorAll('.filter-btn').forEach(btn =>
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            filterTests();
        })
    );

    // сброс всех фильтров
    resetBtn?.addEventListener("click", () => {
        searchInput.value = "";
        clearSelect(statusFilter);
        clearSelect(moduleFilter);

        document.querySelectorAll(".filter-btn").forEach(btn => btn.classList.remove("active"));
        document.querySelector('.filter-btn[data-filter="all"]')?.classList.add("active");

        filterTests();
    });

    filterTests();
}

function getSelectedValues(select) {
    if (!select) return [];
    const values = select.multiple
        ? Array.from(select.selectedOptions).map(o => o.value)
        : select.value ? [select.value] : [];

    return values
        .map(v => v.toString().trim())
        .filter(v => v && v.toLowerCase() !== 'all');
}

function clearSelect(select) {
    if (!select) return;
    if (select.multiple) {
        Array.from(select.options).forEach(o => o.selected = false);
    } else {
        const hasAll = Array.from(select.options).some(o => o.value.toLowerCase() === 'all');
        select.value = hasAll ? 'all' : '';
    }
}

function normalizeStatus(s) {
    return (s ?? '').toString().trim().toUpperCase();
}

function matchesFilters(nameLC, statusRaw, moduleName, filters) {
    const statusU = normalizeStatus(statusRaw);
    return !(
        (filters.search && !nameLC.includes(filters.search)) ||
        (filters.status.length && !filters.status.includes(statusU)) ||
        (filters.module.length && !filters.module.includes(moduleName)) ||
        (filters.buttonStatuses.length && !filters.buttonStatuses.includes(statusU.toLowerCase()))
    );
}

function filterTests() {
    const search = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
    const statusSelected = getSelectedValues(document.getElementById('statusFilter')).map(v => v.toUpperCase());
    const moduleSelected = getSelectedValues(document.getElementById('moduleFilter'));
    const activeButtons = Array.from(document.querySelectorAll('.filter-btn.active'))
        .map(b => b.dataset.filter?.toLowerCase().trim())
        .filter(f => f && f !== 'all');

    const filters = { search, status: statusSelected, module: moduleSelected, buttonStatuses: activeButtons };

    let modulesVisible = 0;
    document.querySelectorAll('.module').forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        let moduleHasVisible = false;

        moduleEl.querySelectorAll('.test').forEach(test => {
            const testName = (test.dataset.test || '').toLowerCase();
            const isGroup  = test.classList.contains('test-multi');
            let visible = false;

            if (isGroup) {
                let subVisible = 0;
                test.querySelectorAll('.test-sub').forEach(sub => {
                    const subName = (sub.dataset.test || '').toLowerCase();
                    const subStatus = sub.dataset.status;
                    const show = matchesFilters(subName, subStatus, moduleName, filters);
                    sub.style.display = show ? 'block' : 'none';
                    if (show) subVisible++;
                });
                visible = subVisible > 0;
            } else {
                visible = matchesFilters(testName, test.dataset.status, moduleName, filters);
            }

            test.style.display = visible ? 'block' : 'none';
            if (visible) moduleHasVisible = true;
        });

        moduleEl.style.display = moduleHasVisible ? 'block' : 'none';
        if (moduleHasVisible) modulesVisible++;
    });

    const main = document.querySelector('.main-content');
    let noResults = document.getElementById('noResults');
    if (modulesVisible === 0) {
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'noResults';
            noResults.className = 'no-results';
            noResults.innerHTML = '<i class="fas fa-search"></i><br>No tests match your filters';
            main.appendChild(noResults);
        }
    } else {
        noResults?.remove();
    }
}


// ======================================================
//  UI-Toggles
// ======================================================

function toggleBlock(header) {
    const content = header.nextElementSibling;
    if (!content) return;
    content.classList.toggle('active');
    header.classList.toggle('expanded');
}

function toggleStacktrace(el) {
    el.classList.toggle("expanded");
    el.nextElementSibling?.classList.toggle("active");
}

function toggleStep(header) {
    const step = header.closest('.step');
    if (!step) return;

    const body = step.querySelector('.step-body');
    const content = step.querySelector('.step-content');
    const isActive = header.classList.contains('expanded');

    body?.classList.toggle('active', !isActive);
    header.classList.toggle('expanded', !isActive);
    content?.classList.toggle('expanded', !isActive);
    content?.classList.toggle('active', !isActive);
}

function switchTab(btn, tabName) {
    const tabsContainer = btn.closest('.tabs');
    if (!tabsContainer) return;

    tabsContainer.querySelectorAll('.tab-btn').forEach(tab => tab.classList.remove('active'));
    tabsContainer.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    btn.classList.add('active');
    tabsContainer.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
}


// ======================================================
//  Attachment Modal
// ======================================================

const modal          = document.getElementById('attachmentModal');
const title          = document.getElementById('modalTitle');
const image          = document.getElementById('modalImage');
const imageContainer = document.getElementById('imageContainer');
const textPreview    = document.getElementById('modalText');
const pdfContainer   = document.getElementById('modalPDF');
const download       = document.getElementById('modalDownload');

let scale = 1;

function openAttachment(name, type) {
    const path = `./attachments/${name}`;

    // Сброс состояния
    scale = 1;
    [image, pdfContainer, textPreview].forEach(el => el.src = '');
    [imageContainer, textPreview, pdfContainer, download].forEach(el => el.style.display = 'none');
    image.style.transform = 'scale(1)';
    title.textContent = name;

    if (type.startsWith('image/')) {
        image.src = path;
        imageContainer.style.display = 'block';
    } else if (type === 'application/pdf') {
        pdfContainer.src = path;
        pdfContainer.style.display = 'block';
    } else if (type.startsWith('text/') || /\.(json|log|txt|py|md)$/i.test(name)) {
        fetch(path)
            .then(res => res.text())
            .then(text => {
                textPreview.textContent = text;
                textPreview.style.display = 'block';
            })
            .catch(() => {
                textPreview.textContent = '[Ошибка загрузки текста]';
                textPreview.style.display = 'block';
            });
    } else {
        download.href = path;
        download.style.display = 'inline-block';
    }

    modal.style.display = 'block';
}

function closeModal(event) {
    if (event.target.id === 'attachmentModal' || event.target.classList.contains('close')) {
        modal.style.display = 'none';
    }
}

// --- Zoom + Drag ---
imageContainer.addEventListener('wheel', (e) => {
    e.preventDefault();
    scale = Math.min(Math.max(scale + e.deltaY * -0.001, 0.5), 5);
    image.style.transform = `scale(${scale})`;
});

let isDragging = false, startX, startY, scrollLeft, scrollTop;

imageContainer.addEventListener('mousedown', e => {
    isDragging = true;
    startX = e.pageX;
    startY = e.pageY;
    scrollLeft = imageContainer.scrollLeft;
    scrollTop = imageContainer.scrollTop;
    imageContainer.style.cursor = 'grabbing';
});

imageContainer.addEventListener('mousemove', e => {
    if (!isDragging) return;
    imageContainer.scrollLeft = scrollLeft - (e.pageX - startX);
    imageContainer.scrollTop  = scrollTop - (e.pageY - startY);
});

['mouseup', 'mouseleave'].forEach(evt =>
    imageContainer.addEventListener(evt, () => {
        isDragging = false;
        imageContainer.style.cursor = 'grab';
    })
);


// ======================================================
//  Theme
// ======================================================

const root = document.documentElement;
const themeToggle = document.getElementById("themeToggle");
const savedTheme = localStorage.getItem("theme");

root.setAttribute(
    "data-theme",
    savedTheme || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
);

themeToggle?.addEventListener("click", () => {
    const newTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
});


// ======================================================
//  Navigation
// ======================================================

function toggleTestAndHash(header) {
    const el = header.closest(".test, .card");
    if (!el?.id) return;

    const content = header.nextElementSibling;
    const isOpening = !content.classList.contains("active");

    toggleBlock(header);

    history.pushState(
        isOpening ? { openedId: el.id } : {},
        "",
        isOpening ? `#${el.id}` : location.pathname + location.search
    );
}

function expandTestAndParents(el) {
    let current = el;
    while (current) {
        const header = current.querySelector(":scope > .test-header, :scope > .test-header-multi, :scope > .header");
        const content = current.querySelector(":scope > .test-content, :scope > .content");
        header?.classList.add("expanded");
        content?.classList.add("active");
        current = current.parentElement.closest(".test, .card");
    }
}

function resetAllBlocks() {
    document.querySelectorAll(".test-content, .content").forEach(c => c.classList.remove("active"));
    document.querySelectorAll(".test-header, .test-header-multi").forEach(h => h.classList.remove("expanded"));
}

window.addEventListener("load", () => {
    const hash = location.hash.slice(1);
    if (!hash) return;
    const el = document.getElementById(hash);
    if (el) {
        el.classList.add("highlight");
        el.scrollIntoView({ behavior: "smooth" });
        expandTestAndParents(el);
    }
});

window.addEventListener("popstate", event => {
    const id = event.state?.openedId;
    if (!id) return;
    const el = document.getElementById(id);
    if (el) {
        el.classList.add("highlight");
        el.scrollIntoView({ behavior: "smooth" });
        expandTestAndParents(el);
    }
});


// ======================================================
//  Init
// ======================================================

document.addEventListener('DOMContentLoaded', initFilters);
