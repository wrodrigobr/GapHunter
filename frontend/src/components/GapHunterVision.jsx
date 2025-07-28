import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';

const GapHunterVision = () => {
  const [activeTab, setActiveTab] = useState('settings');
  const [visionSettings, setVisionSettings] = useState({
    is_profile_public: false,
    allow_gap_analysis: false,
    show_performance_stats: false,
    show_recent_hands: false,
    hide_real_name: true,
    hide_earnings: true
  });
  const [publicPlayers, setPublicPlayers] = useState([]);
  const [myAnalyses, setMyAnalyses] = useState({ analyses_made: [], analyses_received: [] });
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(true);

  const [newAnalysis, setNewAnalysis] = useState({
    notes: '',
    identified_gaps: [],
    strengths: '',
    recommendations: '',
    hands_analyzed: 0,
    confidence_score: 0
  });

  useEffect(() => {
    loadVisionData();
  }, []);

  const loadVisionData = async () => {
    try {
      setLoading(true);
      
      // Carregar configurações
      const settingsResponse = await api.get('/coaching/vision/settings');
      setVisionSettings(settingsResponse.data);

      // Carregar jogadores públicos
      const playersResponse = await api.get('/coaching/vision/players');
      setPublicPlayers(playersResponse.data.players);

      // Carregar minhas análises
      const analysesResponse = await api.get('/coaching/vision/analyses');
      setMyAnalyses(analysesResponse.data);

    } catch (error) {
      console.error('Erro ao carregar dados do Vision:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateVisionSettings = async (newSettings) => {
    try {
      await api.put('/coaching/vision/settings', newSettings);
      setVisionSettings(newSettings);
    } catch (error) {
      console.error('Erro ao atualizar configurações:', error);
    }
  };

  const analyzePlayer = async (e) => {
    e.preventDefault();
    if (!selectedPlayer) return;

    try {
      await api.post('/coaching/vision/analyze', {
        target_id: selectedPlayer.id,
        ...newAnalysis
      });

      setNewAnalysis({
        notes: '',
        identified_gaps: [],
        strengths: '',
        recommendations: '',
        hands_analyzed: 0,
        confidence_score: 0
      });
      setSelectedPlayer(null);
      
      // Recarregar análises
      const analysesResponse = await api.get('/coaching/vision/analyses');
      setMyAnalyses(analysesResponse.data);
    } catch (error) {
      console.error('Erro ao criar análise:', error);
      alert('Erro ao criar análise. Verifique se ambos os perfis são públicos.');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-white">Carregando GapHunter Vision...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">GapHunter Vision</h2>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 rounded ${activeTab === 'settings' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Configurações
          </button>
          <button
            onClick={() => setActiveTab('players')}
            className={`px-4 py-2 rounded ${activeTab === 'players' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Jogadores Públicos
          </button>
          <button
            onClick={() => setActiveTab('analyses')}
            className={`px-4 py-2 rounded ${activeTab === 'analyses' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Minhas Análises
          </button>
        </div>
      </div>

      {/* Aba de Configurações */}
      {activeTab === 'settings' && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">Configurações de Privacidade</h3>
          <p className="text-gray-300 mb-6">
            O GapHunter Vision funciona com base na reciprocidade: para analisar outros jogadores, 
            você também deve tornar seu perfil público.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Perfil Público</h4>
                <p className="text-gray-400 text-sm">Permite que outros jogadores vejam seu perfil</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.is_profile_public}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    is_profile_public: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Permitir Análise de Gaps</h4>
                <p className="text-gray-400 text-sm">Outros jogadores podem analisar seus gaps</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.allow_gap_analysis}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    allow_gap_analysis: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Mostrar Estatísticas de Performance</h4>
                <p className="text-gray-400 text-sm">Exibe ROI, ITM% e outras estatísticas</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.show_performance_stats}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    show_performance_stats: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Mostrar Mãos Recentes</h4>
                <p className="text-gray-400 text-sm">Permite visualizar suas mãos recentes</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.show_recent_hands}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    show_recent_hands: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Ocultar Nome Real</h4>
                <p className="text-gray-400 text-sm">Mostra apenas um ID anônimo</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.hide_real_name}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    hide_real_name: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-700 rounded">
              <div>
                <h4 className="text-white font-medium">Ocultar Ganhos</h4>
                <p className="text-gray-400 text-sm">Não mostra valores financeiros específicos</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={visionSettings.hide_earnings}
                  onChange={(e) => updateVisionSettings({
                    ...visionSettings,
                    hide_earnings: e.target.checked
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Aba de Jogadores Públicos */}
      {activeTab === 'players' && (
        <div className="space-y-6">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Jogadores com Perfil Público</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {publicPlayers.map((player) => (
                <div key={player.id} className="bg-gray-700 p-4 rounded-lg">
                  <h4 className="font-semibold text-white">{player.username}</h4>
                  <div className="text-sm text-gray-400 mb-3">
                    Membro desde: {formatDate(player.member_since)}
                  </div>

                  {/* Estatísticas de Performance */}
                  {player.performance_stats && (
                    <div className="mb-3 space-y-1">
                      <div className="text-xs text-gray-400">Performance (30 dias):</div>
                      <div className="text-sm text-white">
                        ROI: <span className={player.performance_stats.roi_percentage >= 0 ? 'text-green-400' : 'text-red-400'}>
                          {player.performance_stats.roi_percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-sm text-white">
                        ITM: {player.performance_stats.itm_percentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-white">
                        Torneios: {player.performance_stats.tournaments_played}
                      </div>
                    </div>
                  )}

                  {/* Resumo de Gaps */}
                  {player.gaps_summary && (
                    <div className="mb-3 space-y-1">
                      <div className="text-xs text-gray-400">Gaps Identificados:</div>
                      <div className="text-sm text-white">
                        Total: {player.gaps_summary.total}
                      </div>
                      {player.gaps_summary.critical > 0 && (
                        <div className="text-sm text-red-400">
                          Críticos: {player.gaps_summary.critical}
                        </div>
                      )}
                      {player.gaps_summary.most_common && (
                        <div className="text-xs text-gray-300">
                          Mais comum: {player.gaps_summary.most_common}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Configurações de Privacidade */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-400 mb-1">Permite:</div>
                    <div className="flex flex-wrap gap-1">
                      {player.privacy_settings.allow_gap_analysis && (
                        <span className="text-xs bg-green-600 px-2 py-1 rounded">Análise</span>
                      )}
                      {player.privacy_settings.show_performance && (
                        <span className="text-xs bg-blue-600 px-2 py-1 rounded">Performance</span>
                      )}
                      {player.privacy_settings.show_recent_hands && (
                        <span className="text-xs bg-purple-600 px-2 py-1 rounded">Mãos</span>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => setSelectedPlayer(player)}
                    disabled={!player.privacy_settings.allow_gap_analysis}
                    className={`w-full py-2 rounded text-sm ${
                      player.privacy_settings.allow_gap_analysis
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {player.privacy_settings.allow_gap_analysis ? 'Analisar Jogador' : 'Análise Não Permitida'}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Modal de Análise */}
          {selectedPlayer && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-gray-800 p-6 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Analisar {selectedPlayer.username}
                </h3>
                <form onSubmit={analyzePlayer} className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Notas Gerais</label>
                    <textarea
                      value={newAnalysis.notes}
                      onChange={(e) => setNewAnalysis({...newAnalysis, notes: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      rows={3}
                      placeholder="Observações gerais sobre o estilo de jogo..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Pontos Fortes</label>
                    <textarea
                      value={newAnalysis.strengths}
                      onChange={(e) => setNewAnalysis({...newAnalysis, strengths: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      rows={2}
                      placeholder="Aspectos positivos do jogo..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Recomendações</label>
                    <textarea
                      value={newAnalysis.recommendations}
                      onChange={(e) => setNewAnalysis({...newAnalysis, recommendations: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      rows={2}
                      placeholder="Sugestões de melhoria..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Mãos Analisadas</label>
                      <input
                        type="number"
                        value={newAnalysis.hands_analyzed}
                        onChange={(e) => setNewAnalysis({...newAnalysis, hands_analyzed: parseInt(e.target.value)})}
                        className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Confiança (0-100)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={newAnalysis.confidence_score}
                        onChange={(e) => setNewAnalysis({...newAnalysis, confidence_score: parseFloat(e.target.value)})}
                        className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      />
                    </div>
                  </div>
                  <div className="flex gap-4 pt-4">
                    <button
                      type="submit"
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
                    >
                      Criar Análise
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedPlayer(null)}
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
      )}

      {/* Aba de Análises */}
      {activeTab === 'analyses' && (
        <div className="space-y-6">
          {/* Análises Feitas */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Análises que Fiz</h3>
            {myAnalyses.analyses_made.length > 0 ? (
              <div className="space-y-3">
                {myAnalyses.analyses_made.map((analysis) => (
                  <div key={analysis.id} className="bg-gray-700 p-4 rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-white">{analysis.target_username}</h4>
                        <div className="text-sm text-gray-400">
                          {formatDate(analysis.created_at)} - {analysis.hands_analyzed} mãos analisadas
                        </div>
                        <div className="text-sm text-gray-400">
                          Confiança: {analysis.confidence_score}%
                        </div>
                      </div>
                      <div className="text-sm text-blue-400">
                        {analysis.analysis_type}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">
                Você ainda não fez nenhuma análise
              </div>
            )}
          </div>

          {/* Análises Recebidas */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Análises que Recebi</h3>
            {myAnalyses.analyses_received.length > 0 ? (
              <div className="space-y-3">
                {myAnalyses.analyses_received.map((analysis) => (
                  <div key={analysis.id} className="bg-gray-700 p-4 rounded">
                    <div className="mb-2">
                      <h4 className="font-medium text-white">Por: {analysis.analyzer_username}</h4>
                      <div className="text-sm text-gray-400">
                        {formatDate(analysis.created_at)}
                      </div>
                    </div>
                    {analysis.notes && (
                      <div className="mb-2">
                        <div className="text-sm text-gray-400">Notas:</div>
                        <div className="text-sm text-white">{analysis.notes}</div>
                      </div>
                    )}
                    {analysis.strengths && (
                      <div className="mb-2">
                        <div className="text-sm text-gray-400">Pontos Fortes:</div>
                        <div className="text-sm text-green-400">{analysis.strengths}</div>
                      </div>
                    )}
                    {analysis.recommendations && (
                      <div className="mb-2">
                        <div className="text-sm text-gray-400">Recomendações:</div>
                        <div className="text-sm text-blue-400">{analysis.recommendations}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400 text-center py-8">
                Você ainda não recebeu nenhuma análise
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GapHunterVision;

