import { loadCSV } from '../utils/csv.js';
import { datasetMissing, getColorByIndex, numberFormatter } from '../utils/helpers.js';

const DATASET_PATH = 'datasets/dist_percentual_progresso.csv';

export async function renderProgressoChart() {
  const canvas = document.getElementById('chartProgresso');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('dist_percentual_progresso.csv');
    return;
  }

  if (!rows.length) {
    datasetMissing('dist_percentual_progresso.csv');
    return;
  }

  const labels = rows.map((row) => row.Bucket_Progresso || row.bucket_progresso);
  const counts = rows.map((row) => Number(row.qtd || row.Qtd || 0));

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Alunos',
          data: counts,
          backgroundColor: labels.map((_, index) => getColorByIndex(index)),
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.x ?? 0;
              return `${numberFormatter.format(value)} alunos`;
            },
          },
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
        y: { title: { display: true, text: 'Faixa de Progresso' } },
      },
    },
  });
}
