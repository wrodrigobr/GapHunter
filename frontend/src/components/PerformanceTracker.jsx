import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';

const PerformanceTracker = () => {
  const [stats, setStats] = useState(null);
  const [tournaments, setTournaments] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [showAddTournament, setShowAddTournament] = useState(false);

  const [newTournament, setNewTournament] = useState({
    tournament_id: '',
    name: '',
    buy_in: '',
    prize: '',
    position: '',
    players_count: ''
  });

  useEffect(() => {
    loadPerformanceData();
  }, [selectedPeriod]);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      
      // Carregar estatísticas
      const statsResponse = await api.get(`/performance/stats?days_back=${selectedPeriod}`);
      setStats(statsResponse.data.stats);

      // Carregar torneios
      const tournamentsResponse = await api.get('/performance/tournaments?limit=20');
      setTournaments(tournamentsResponse.data.tournaments);

      // Carregar dados do gráfico
      const chartResponse = await api.get(`/performance/roi-chart?days_back=${selectedPeriod}`);
      setChartData(chartResponse.data.chart_data);

    } catch (error) {
      console.error('Erro ao carregar dados de performance:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTournament = async (e) => {
    e.preventDefault();
    try {
      await api.post('/performance/tournaments', {
        ...newTournament,
        buy_in: parseFloat(newTournament.buy_in),
        prize: parseFloat(newTournament.prize),
        position: parseInt(newTournament.position) || null,
        players_count: parseInt(newTournament.players_count) || null
      });

      setNewTournament({
        tournament_id: '',
        name: '',
        buy_in: '',
        prize: '',
        position: '',
        players_count: ''
      });
      setShowAddTournament(false);
      loadPerformanceData();
    } catch (error) {
      console.error('Erro ao adicionar torneio:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando dados de performance...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">ROI & Performance Tracker</h2>
        <div className="flex gap-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(parseInt(e.target.value))}
            className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
          >
            <option value={7}>Últimos 7 dias</option>
            <option value={30}>Últimos 30 dias</option>
            <option value={90}>Últimos 90 dias</option>
            <option value={365}>Último ano</option>
          </select>
          <button
            onClick={() => setShowAddTournament(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Adicionar Torneio
          </button>
        </div>
      </div>

      {/* Estatísticas Principais */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm text-gray-400 mb-2">ROI</h3>
            <div className={`text-2xl font-bold ${stats.roi_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPercentage(stats.roi_percentage)}
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm text-gray-400 mb-2">Lucro/Prejuízo</h3>
            <div className={`text-2xl font-bold ${stats.net_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatCurrency(stats.net_profit)}
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm text-gray-400 mb-2">ITM%</h3>
            <div className="text-2xl font-bold text-white">
              {stats.itm_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">
              {stats.itm_count}/{stats.tournaments_played} torneios
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm text-gray-400 mb-2">Volume</h3>
            <div className="text-2xl font-bold text-white">
              {stats.tournaments_played}
            </div>
            <div className="text-sm text-gray-400">
              {formatCurrency(stats.total_buy_ins)} investidos
            </div>
          </div>
        </div>
      )}

      {/* Gráfico de ROI */}
      {chartData.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">Evolução do ROI</h3>
          <div className="h-64 flex items-end justify-between space-x-1">
            {chartData.slice(-20).map((point, index) => (
              <div key={index} className="flex flex-col items-center">
                <div
                  className={`w-4 ${point.roi >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{
                    height: `${Math.abs(point.roi) * 2 + 10}px`,
                    minHeight: '10px'
                  }}
                  title={`${point.date}: ${formatPercentage(point.roi)}`}
                />
                <div className="text-xs text-gray-400 mt-1 transform rotate-45">
                  {point.date.split('-')[2]}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estatísticas Detalhadas */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Estatísticas Financeiras</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Buy-ins Totais:</span>
                <span className="text-white">{formatCurrency(stats.total_buy_ins)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Premiações Totais:</span>
                <span className="text-white">{formatCurrency(stats.total_prizes)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Buy-in Médio:</span>
                <span className="text-white">{formatCurrency(stats.avg_buy_in)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Maior Premiação:</span>
                <span className="text-green-400">{formatCurrency(stats.biggest_win)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Lucro por Torneio:</span>
                <span className={stats.profit_per_tournament >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {formatCurrency(stats.profit_per_tournament)}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Estatísticas de Posicionamento</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Posição Média:</span>
                <span className="text-white">{stats.avg_finish_position.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Melhor Posição:</span>
                <span className="text-green-400">{stats.best_finish}º</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Pior Posição:</span>
                <span className="text-red-400">{stats.worst_finish}º</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">ITM Count:</span>
                <span className="text-white">{stats.itm_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">ITM Rate:</span>
                <span className="text-white">{stats.itm_percentage.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Torneios Recentes */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Torneios Recentes</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="text-left py-2">Data</th>
                <th className="text-left py-2">Torneio</th>
                <th className="text-right py-2">Buy-in</th>
                <th className="text-right py-2">Posição</th>
                <th className="text-right py-2">Premiação</th>
                <th className="text-right py-2">ROI</th>
              </tr>
            </thead>
            <tbody>
              {tournaments.slice(0, 10).map((tournament) => (
                <tr key={tournament.id} className="border-b border-gray-700">
                  <td className="py-2 text-gray-300">
                    {new Date(tournament.date_played).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="py-2 text-white">
                    {tournament.name}
                    {tournament.is_itm && <span className="ml-2 text-xs bg-green-600 px-2 py-1 rounded">ITM</span>}
                  </td>
                  <td className="py-2 text-right text-white">
                    {formatCurrency(tournament.buy_in)}
                  </td>
                  <td className="py-2 text-right text-white">
                    {tournament.position || '-'}
                  </td>
                  <td className="py-2 text-right text-white">
                    {formatCurrency(tournament.prize)}
                  </td>
                  <td className={`py-2 text-right ${tournament.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatPercentage(tournament.roi)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Adicionar Torneio */}
      {showAddTournament && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Adicionar Torneio</h3>
            <form onSubmit={handleAddTournament} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">ID do Torneio</label>
                <input
                  type="text"
                  value={newTournament.tournament_id}
                  onChange={(e) => setNewTournament({...newTournament, tournament_id: e.target.value})}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Nome</label>
                <input
                  type="text"
                  value={newTournament.name}
                  onChange={(e) => setNewTournament({...newTournament, name: e.target.value})}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Buy-in ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newTournament.buy_in}
                    onChange={(e) => setNewTournament({...newTournament, buy_in: e.target.value})}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Premiação ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newTournament.prize}
                    onChange={(e) => setNewTournament({...newTournament, prize: e.target.value})}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Posição Final</label>
                  <input
                    type="number"
                    value={newTournament.position}
                    onChange={(e) => setNewTournament({...newTournament, position: e.target.value})}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Jogadores</label>
                  <input
                    type="number"
                    value={newTournament.players_count}
                    onChange={(e) => setNewTournament({...newTournament, players_count: e.target.value})}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  />
                </div>
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
                >
                  Adicionar
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddTournament(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceTracker;

