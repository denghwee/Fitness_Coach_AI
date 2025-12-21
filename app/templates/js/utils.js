// format workout plan -> HTML string
function formatWorkoutPlan(plan) {
  if (!plan || !plan.weekly_schedule) return '<div class="no-plan">No workout plan available.</div>';

  const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  let html = '<div class="workout-plan">';

  html += '<h3>Weekly Workout Plan</h3>';
  days.forEach(day => {
    const block = plan.weekly_schedule[day];
    if (!block) return;
    html += `<section class="workout-day"><h4>${day} — ${escapeHtml(block.workout_type || '')}</h4>`;
    if (block.exercises && block.exercises.length) {
      html += '<ul class="exercises">';
      block.exercises.forEach(ex => {
        const name = escapeHtml(ex.name || '');
        const sets = ex.sets ? `${ex.sets} x ${ex.reps || ''}`.trim() : null;
        const dur = ex.duration ? escapeHtml(ex.duration) : null;
        html += `<li class="exercise"><strong>${name}</strong>${sets ? ' — ' + sets : ''}${dur ? ' — ' + dur : ''}</li>`;
      });
      html += '</ul>';
    } else if (block.notes) {
      html += `<p class="notes">${escapeHtml(block.notes)}</p>`;
    }
    html += '</section>';
  });

  if (plan.explanation) {
    html += `<div class="explanation"><h4>Explanation</h4><p>${escapeHtml(plan.explanation)}</p></div>`;
  }
  html += `<div class="disclaimer">Disclaimer: ${escapeHtml(plan.disclaimer || 'Consult a professional before starting a new exercise program.')}</div>`;
  html += '</div>';
  return html;
}

// small helper to avoid injecting raw HTML
function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}