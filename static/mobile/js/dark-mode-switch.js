'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const toggleSwitch = document.getElementById('darkSwitch');
  const currentTheme = localStorage.getItem('theme');

  if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (currentTheme === 'dark' && toggleSwitch) {
      toggleSwitch.checked = true;
    }
  }

  function switchTheme(e) {
    const theme = e.target.checked ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }

  if (toggleSwitch) {
    toggleSwitch.addEventListener('change', switchTheme);
  }

});

// Demo version dark mode checkbox

const toggleSwitch2 = document.getElementById('darkSwitch2');

if (toggleSwitch2) {
  document.addEventListener('DOMContentLoaded', function () {
    const nightMode = document.getElementById('nightMode');
    const dayMode = document.getElementById('dayMode');
    const currentTheme = localStorage.getItem('theme');

    function updateModeDisplay(isDarkMode) {
      if (isDarkMode) {
        nightMode.classList.add('d-none');
        dayMode.classList.remove('d-none');
      } else {
        nightMode.classList.remove('d-none');
        dayMode.classList.add('d-none');
      }
    }

    if (currentTheme) {
      const isDarkMode = currentTheme === 'dark';
      document.documentElement.setAttribute('data-theme', currentTheme);
      toggleSwitch2.checked = isDarkMode;
      updateModeDisplay(isDarkMode);
    }

    function switchTheme(e) {
      const isDarkMode = e.target.checked;
      const theme = isDarkMode ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      updateModeDisplay(isDarkMode);
      location.reload();
    }

    toggleSwitch2.addEventListener('change', switchTheme);
  });
}