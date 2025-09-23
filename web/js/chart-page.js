import { renderSituacaoChart } from './charts/situacao.js';
import { renderModalidadeChart } from './charts/modalidade.js';
import { renderTurnoChart } from './charts/turno.js';
import { renderProgressoChart } from './charts/progresso.js';
import { renderFormaIngressoChart } from './charts/forma_ingresso.js';
import { renderCotasChart } from './charts/cotas.js';
import { renderEtniaChart } from './charts/etnia.js';
import { renderNecessidadesChart } from './charts/necessidades.js';
import { renderTipoEscolaChart } from './charts/tipo_escola.js';
import { renderNaturezaChart } from './charts/natureza.js';
import { renderTransporteChart } from './charts/transporte.js';
import { datasetMissing } from './utils/helpers.js';

const chartMap = {
  situacao: {
    title: 'Situação dos Alunos',
    canvasId: 'chartSituacao',
    render: renderSituacaoChart,
  },
  modalidade: {
    title: 'Modalidades dos Cursos',
    canvasId: 'chartModalidade',
    render: renderModalidadeChart,
  },
  turno: {
    title: 'Distribuição por Turno',
    canvasId: 'chartTurno',
    render: renderTurnoChart,
  },
  progresso: {
    title: 'Progresso no Curso',
    canvasId: 'chartProgresso',
    render: renderProgressoChart,
  },
  forma_ingresso: {
    title: 'Formas de Ingresso',
    canvasId: 'chartFormaIngresso',
    render: renderFormaIngressoChart,
  },
  cotas: {
    title: 'Cotas (MEC/Sistec)',
    canvasId: 'chartCotas',
    render: renderCotasChart,
  },
  etnia: {
    title: 'Etnia/Raça',
    canvasId: 'chartEtnia',
    render: renderEtniaChart,
  },
  necessidades: {
    title: 'Necessidades Especiais',
    canvasId: 'chartNecessidades',
    render: renderNecessidadesChart,
  },
  tipo_escola: {
    title: 'Tipo de Escola de Origem',
    canvasId: 'chartTipoEscola',
    render: renderTipoEscolaChart,
  },
  natureza: {
    title: 'Natureza de Participação',
    canvasId: 'chartNatureza',
    render: renderNaturezaChart,
  },
  transporte: {
    title: 'Transporte Escolar',
    canvasId: 'chartTransporte',
    render: renderTransporteChart,
  },
};

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function renderSelectedChart(key) {
  const normalizedKey = (key || '').trim().toLowerCase();
  const config = chartMap[normalizedKey];
  if (!config) {
    datasetMissing(`chart desconhecido: ${key}`);
    document.getElementById('chartTitle').textContent = 'Gráfico não encontrado';
    return;
  }

  const canvas = document.getElementById('singleChartCanvas');
  if (!canvas) {
    datasetMissing('canvas não encontrado');
    return;
  }

  canvas.id = config.canvasId;
  document.getElementById('chartTitle').textContent = config.title;

  Promise.resolve(config.render()).catch((error) => {
    console.error('Falha ao renderizar gráfico', error);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  const key = getQueryParam('chart');
  if (!key) {
    datasetMissing('param chart ausente');
    document.getElementById('chartTitle').textContent = 'Escolha um gráfico no painel';
    return;
  }
  renderSelectedChart(key);
});
