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
import { renderNaturezaEscolaChart } from './charts/natureza_escola.js';
import { renderSituacaoEscolaChart } from './charts/situacao_escola.js';

function loadCharts() {
  const loaders = [
    renderSituacaoChart(),
    renderModalidadeChart(),
    renderTurnoChart(),
    renderProgressoChart(),
    renderFormaIngressoChart(),
    renderCotasChart(),
    renderEtniaChart(),
    renderNecessidadesChart(),
    renderTipoEscolaChart(),
    renderNaturezaChart(),
    renderTransporteChart(),
    renderNaturezaEscolaChart(),
    renderSituacaoEscolaChart(),
  ];

  Promise.allSettled(loaders).catch((error) => {
    console.error('Falha ao carregar os gráficos', error);
  });
}

document.addEventListener('DOMContentLoaded', loadCharts);
