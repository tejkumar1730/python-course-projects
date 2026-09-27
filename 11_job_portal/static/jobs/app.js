// Small progressive enhancements. All validation still runs on the server.
const roleInput = document.getElementById('id_role');
const companyField = document.querySelector('[data-field="company_name"]');
if (roleInput && companyField) {
  const updateCompanyField = () => {
    companyField.hidden = roleInput.value !== 'employer';
    companyField.querySelector('input').required = roleInput.value === 'employer';
  };
  roleInput.addEventListener('change', updateCompanyField);
  updateCompanyField();
}
const letter = document.getElementById('id_cover_letter');
const counter = document.getElementById('letter-counter');
if (letter && counter) {
  const updateCount = () => { counter.textContent = `${letter.value.length} / 3000 characters · Minimum 30`; };
  letter.addEventListener('input', updateCount);
  updateCount();
}
