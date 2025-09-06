function initFilters() {
    const searchInput  = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const moduleFilter = document.getElementById('moduleFilter');

    searchInput?.addEventListener('input', filterTests);
    statusFilter?.addEventListener('change', filterTests);
    moduleFilter?.addEventListener('change', filterTests);

    searchInput?.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            filterTests();
        }
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.toggle('active');
            filterTests();
        });
    });

    document.getElementById("reset-filters").addEventListener("click", () => {
        searchInput.value = "";

        clearSelect(statusFilter);
        clearSelect(moduleFilter);

        document.querySelectorAll(".filter-btn").forEach(btn => {
            btn.classList.remove("active");
        });
        document.querySelector('.filter-btn[data-filter="all"]')?.classList.add("active");

        filterTests();
    });

    filterTests();
}


function getSelectedValues(select) {
    if (!select) return [];
    let values = [];
    if (select.multiple) {
        values = Array.from(select.selectedOptions).map(o => o.value);
    } else {
        if (select.value) values = [select.value];
    }
    return values
        .map(v => (v ?? '').toString().trim())
        .filter(v => v && v.toLowerCase() !== 'all');
}


function clearSelect(select) {
    if (!select) return;
    if (select.multiple) {
        Array.from(select.options).forEach(o => (o.selected = false));
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
    if (filters.search && !nameLC.includes(filters.search)) return false;
    if (filters.status.length && !filters.status.includes(statusU)) return false;
    if (filters.module.length && !filters.module.includes(moduleName)) return false;
    if (filters.buttonStatuses.length && !filters.buttonStatuses.includes(statusU.toLowerCase())) return false;
    return true;
}


function filterTests() {
    const search = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
    const statusSelected = getSelectedValues(document.getElementById('statusFilter')).map(v => v.toUpperCase());
    const moduleSelected = getSelectedValues(document.getElementById('moduleFilter'));
    const activeButtons = Array.from(document.querySelectorAll('.filter-btn.active'))
        .map(b => (b.dataset.filter || '').toLowerCase().trim())
        .filter(f => f && f !== 'all');

    const filters = {
        search,
        status: statusSelected,
        module: moduleSelected,
        buttonStatuses: activeButtons
    };

    const modules = document.querySelectorAll('.module');
    let modulesVisible = 0;

    modules.forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        const tests = moduleEl.querySelectorAll('.test');
        let moduleHasVisible = false;

        tests.forEach(test => {
            const isGroup  = test.classList.contains('test-multi');
            const testName = (test.dataset.test || '').toLowerCase();
            let visible = false;

            if (isGroup) {
                let subVisible = 0;
                test.querySelectorAll('.test-sub').forEach(sub => {
                    const subName   = (sub.dataset.test || '').toLowerCase();
                    const subStatus = sub.dataset.status;
                    const show = matchesFilters(subName, subStatus, moduleName, filters);
                    sub.style.display = show ? 'block' : 'none';
                    if (show) subVisible++;
                });
                visible = subVisible > 0;
            } else {
                const testStatus = test.dataset.status;
                visible = matchesFilters(testName, testStatus, moduleName, filters);
            }

            test.style.display = visible ? 'block' : 'none';
            if (visible) moduleHasVisible = true;
        });

        moduleEl.style.display = moduleHasVisible ? 'block' : 'none';
        if (moduleHasVisible) modulesVisible++;
    });

    let noResults = document.getElementById('noResults');
    if (modulesVisible === 0) {
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'noResults';
            noResults.className = 'no-results';
            noResults.innerHTML = '<i class="fas fa-search"></i><br>No tests match your filters';
            document.querySelector('.main-content').appendChild(noResults);
        }
    } else if (noResults) {
        noResults.remove();
    }
}


function toggleCard(header) {
    const content = header.nextElementSibling;
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        header.classList.remove('expanded');
    } else {
        content.classList.add('active');
        header.classList.add('expanded');
    }
}


function toggleTest(header) {
    const content = header.nextElementSibling;
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        header.classList.remove('expanded');
    } else {
        content.classList.add('active');
        header.classList.add('expanded');
    }
}


function toggleTestRun(header) {
    const content = header.nextElementSibling;
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        header.classList.remove('expanded');
    } else {
        content.classList.add('active');
        header.classList.add('expanded');
    }
}


function toggleStep(header) {
    const step = header.closest('.step');
    if (!step) return;

    const body = step.querySelector('.step-body');
    if (!body) return;

    const content = step.querySelector('.step-content');
<!--            const children = step.querySelector('.step-children');-->

    const isActive = header.classList.contains('expanded');
    body.classList.toggle('active', !isActive);
    header.classList.toggle('expanded', !isActive);
    content.classList.toggle('expanded', !isActive);
    content.classList.toggle('active', !isActive);
}


function switchTab(btn, tabName) {
    const tabsContainer = btn.closest('.tabs');
    const tabs = tabsContainer.querySelectorAll('.tab-btn');
    const contents = tabsContainer.querySelectorAll('.tab-content');

    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));

    btn.classList.add('active');
    const targetContent = tabsContainer.querySelector(`[data-tab="${tabName}"]`);
    if (targetContent) targetContent.classList.add('active');
}

const modal = document.getElementById('attachmentModal');
const title = document.getElementById('modalTitle');
const image = document.getElementById('modalImage');
const imageContainer = document.getElementById('imageContainer');
const textPreview = document.getElementById('modalText');
const pdfContainer = document.getElementById('modalPDF');
const download = document.getElementById('modalDownload');

let scale = 1;


function openAttachment(name, type) {
  const path = `./attachments/${name}`;

  // Reset state
  scale = 1;
  image.style.transform = 'scale(1)';
  image.src = '';
  pdfContainer.src = '';
  textPreview.textContent = '';
  [imageContainer, textPreview, pdfContainer, download].forEach(el => el.style.display = 'none');

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

// Zoom + drag
imageContainer.addEventListener('wheel', (e) => {
  e.preventDefault();
  scale += e.deltaY * -0.001;
  scale = Math.min(Math.max(scale, 0.5), 5);
  image.style.transform = `scale(${scale})`;
});

let isDragging = false;
let startX, startY, scrollLeft, scrollTop;

imageContainer.addEventListener('mousedown', (e) => {
  isDragging = true;
  startX = e.pageX;
  startY = e.pageY;
  scrollLeft = imageContainer.scrollLeft;
  scrollTop = imageContainer.scrollTop;
  imageContainer.style.cursor = 'grabbing';
});

imageContainer.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  imageContainer.scrollLeft = scrollLeft - (e.pageX - startX);
  imageContainer.scrollTop = scrollTop - (e.pageY - startY);
});

['mouseup', 'mouseleave'].forEach(evt =>
  imageContainer.addEventListener(evt, () => {
    isDragging = false;
    imageContainer.style.cursor = 'grab';
  })
);

document.addEventListener('DOMContentLoaded', function() {
    initFilters();
});
