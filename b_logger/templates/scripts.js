
function initFilters() {
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const moduleFilter = document.getElementById('moduleFilter');

    searchInput?.addEventListener('input', filterTests);
    statusFilter?.addEventListener('change', filterTests);
    moduleFilter?.addEventListener('change', filterTests);

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterTests();
        });
    });
}


function filterTests() {
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const status = document.getElementById('statusFilter')?.value || 'all';
    const module = document.getElementById('moduleFilter')?.value || 'all';
    const filter = document.querySelector('.filter-btn.active')?.dataset.filter || 'all';
    let visibleCount = 0;

    document.querySelectorAll('.module').forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        const tests = moduleEl.querySelectorAll('.test');
        let moduleVisible = false;

        tests.forEach(test => {
            const isGroup = test.classList.contains('test-multi');
            const testName = test.dataset.test?.toLowerCase() || '';
            let visible = false;

            if (isGroup) {
                const subtests = test.querySelectorAll('.test-sub');
                let subVisible = 0;
                subtests.forEach(sub => {
                    const subStatus = sub.dataset.status;
                    const subName = sub.dataset.test?.toLowerCase() || '';
                    let show = true;
                    if (search && !subName.includes(search)) show = false;
                    if (status !== 'all' && subStatus !== status) show = false;
                    if (module !== 'all' && moduleName !== module) show = false;
                    if (filter !== 'all' && subStatus.toLowerCase() !== filter) show = false;
                    sub.style.display = show ? 'block' : 'none';
                    if (show) subVisible++;
                });
                visible = subVisible > 0;
            } else {
                const testStatus = test.dataset.status;
                visible = true;
                if (search && !testName.includes(search)) visible = false;
                if (status !== 'all' && testStatus !== status) visible = false;
                if (module !== 'all' && moduleName !== module) visible = false;
                if (filter !== 'all' && testStatus.toLowerCase() !== filter) visible = false;
            }

            test.style.display = visible ? 'block' : 'none';
            if (visible) moduleVisible = true;
        });

        moduleEl.style.display = moduleVisible ? 'block' : 'none';
        if (moduleVisible) visibleCount++;
    });

    let noResults = document.getElementById('noResults');
    if (visibleCount === 0) {
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'noResults';
            noResults.className = 'no-results';
            noResults.innerHTML = '<i class="fas fa-search"></i><br>No tests match your filters';
            document.querySelector('.container').appendChild(noResults);
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
