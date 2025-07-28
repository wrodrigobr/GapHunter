import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';

const SubscriptionClub = () => {
  const [activeTab, setActiveTab] = useState('subscription');
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [affiliateStats, setAffiliateStats] = useState(null);
  const [clubStats, setClubStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  const [isAffiliate, setIsAffiliate] = useState(false);
  const [isClubMember, setIsClubMember] = useState(false);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      
      // Carregar planos
      const plansResponse = await api.get('/subscription/plans');
      setPlans(plansResponse.data.plans);

      // Carregar assinatura atual
      const subscriptionResponse = await api.get('/subscription/my-subscription');
      setCurrentSubscription(subscriptionResponse.data.subscription);

      // Tentar carregar dados de afiliado
      try {
        const affiliateResponse = await api.get('/subscription/affiliate/stats');
        setAffiliateStats(affiliateResponse.data);
        setIsAffiliate(true);
      } catch (error) {
        setIsAffiliate(false);
      }

      // Tentar carregar dados do clube
      try {
        const clubResponse = await api.get('/subscription/club/stats');
        setClubStats(clubResponse.data);
        setIsClubMember(true);
        
        // Carregar leaderboard
        const leaderboardResponse = await api.get('/subscription/club/leaderboard');
        setLeaderboard(leaderboardResponse.data.leaderboard);
      } catch (error) {
        setIsClubMember(false);
      }

    } catch (error) {
      console.error('Erro ao carregar dados de assinatura:', error);
    } finally {
      setLoading(false);
    }
  };

  const subscribe = async (planName, isYearly = false) => {
    try {
      await api.post('/subscription/subscribe', {
        plan: planName,
        is_yearly: isYearly
      });
      
      alert('Assinatura criada com sucesso!');
      loadSubscriptionData();
    } catch (error) {
      console.error('Erro ao criar assinatura:', error);
      alert('Erro ao criar assinatura');
    }
  };

  const joinAffiliateProgram = async (isInfluencer = false) => {
    try {
      const response = await api.post('/subscription/affiliate/join', {
        is_influencer: isInfluencer
      });
      
      alert(`Bem-vindo ao programa de afiliados! Seu código: ${response.data.affiliate_code}`);
      loadSubscriptionData();
    } catch (error) {
      console.error('Erro ao ingressar no programa de afiliados:', error);
      alert('Erro ao ingressar no programa de afiliados');
    }
  };

  const joinClub = async () => {
    try {
      await api.post('/subscription/club/join');
      alert('Bem-vindo ao GapHunter Club!');
      loadSubscriptionData();
    } catch (error) {
      console.error('Erro ao ingressar no clube:', error);
      alert('Erro ao ingressar no clube. Verifique se você tem uma assinatura Pro ou superior.');
    }
  };

  const addClubPoints = async (points = 10) => {
    try {
      await api.post(`/subscription/club/add-points?points=${points}&reason=demo`);
      loadSubscriptionData();
    } catch (error) {
      console.error('Erro ao adicionar pontos:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const getPlanColor = (planName) => {
    const colors = {
      free: 'bg-gray-600',
      basic: 'bg-blue-600',
      pro: 'bg-purple-600',
      coach: 'bg-green-600',
      premium: 'bg-yellow-600'
    };
    return colors[planName] || 'bg-gray-600';
  };

  const getLevelColor = (level) => {
    const colors = {
      bronze: 'text-orange-400',
      silver: 'text-gray-300',
      gold: 'text-yellow-400',
      diamond: 'text-blue-400'
    };
    return colors[level] || 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-white">Carregando sistema de assinatura...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Sistema de Assinatura & Club</h2>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('subscription')}
            className={`px-4 py-2 rounded ${activeTab === 'subscription' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Assinatura
          </button>
          <button
            onClick={() => setActiveTab('affiliate')}
            className={`px-4 py-2 rounded ${activeTab === 'affiliate' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Afiliados
          </button>
          <button
            onClick={() => setActiveTab('club')}
            className={`px-4 py-2 rounded ${activeTab === 'club' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            GapHunter Club
          </button>
        </div>
      </div>

      {/* Aba de Assinatura */}
      {activeTab === 'subscription' && (
        <div className="space-y-6">
          {/* Assinatura Atual */}
          {currentSubscription && (
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">Sua Assinatura Atual</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-700 p-4 rounded">
                  <div className="text-sm text-gray-400">Plano Atual</div>
                  <div className="text-xl font-bold text-white capitalize">{currentSubscription.plan}</div>
                </div>
                <div className="bg-gray-700 p-4 rounded">
                  <div className="text-sm text-gray-400">Status</div>
                  <div className="text-xl font-bold text-green-400 capitalize">{currentSubscription.status}</div>
                </div>
                <div className="bg-gray-700 p-4 rounded">
                  <div className="text-sm text-gray-400">Próxima Cobrança</div>
                  <div className="text-xl font-bold text-white">
                    {currentSubscription.next_billing_date ? formatDate(currentSubscription.next_billing_date) : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Planos Disponíveis */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">Planos Disponíveis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plans.map((plan) => (
                <div key={plan.plan} className="bg-gray-700 p-6 rounded-lg relative">
                  <div className={`absolute top-0 left-0 right-0 h-1 ${getPlanColor(plan.plan)} rounded-t-lg`}></div>
                  
                  <h4 className="text-xl font-bold text-white mb-2 capitalize">{plan.name}</h4>
                  
                  <div className="mb-4">
                    <div className="text-2xl font-bold text-white">
                      {formatCurrency(plan.price_monthly)}
                      <span className="text-sm text-gray-400">/mês</span>
                    </div>
                    {plan.price_yearly > 0 && (
                      <div className="text-sm text-gray-400">
                        ou {formatCurrency(plan.price_yearly)}/ano
                      </div>
                    )}
                  </div>

                  <div className="space-y-2 mb-6">
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">Mãos por mês:</span>
                      <span className="ml-2 text-white">
                        {plan.features.max_hands_per_month === -1 ? 'Ilimitado' : plan.features.max_hands_per_month}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">Análises de gaps:</span>
                      <span className="ml-2 text-white">
                        {plan.features.max_gap_analyses === -1 ? 'Ilimitado' : plan.features.max_gap_analyses}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">Performance Tracker:</span>
                      <span className={`ml-2 ${plan.features.performance_tracker ? 'text-green-400' : 'text-red-400'}`}>
                        {plan.features.performance_tracker ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">Módulo Coaching:</span>
                      <span className={`ml-2 ${plan.features.coaching_module ? 'text-green-400' : 'text-red-400'}`}>
                        {plan.features.coaching_module ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">GapHunter Vision:</span>
                      <span className={`ml-2 ${plan.features.gaphunter_vision ? 'text-green-400' : 'text-red-400'}`}>
                        {plan.features.gaphunter_vision ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">IA Avançada:</span>
                      <span className={`ml-2 ${plan.features.ai_advanced ? 'text-green-400' : 'text-red-400'}`}>
                        {plan.features.ai_advanced ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-400">Acesso ao Club:</span>
                      <span className={`ml-2 ${plan.features.club_access ? 'text-green-400' : 'text-red-400'}`}>
                        {plan.features.club_access ? '✓' : '✗'}
                      </span>
                    </div>
                  </div>

                  {plan.plan !== 'free' && (
                    <div className="space-y-2">
                      <button
                        onClick={() => subscribe(plan.plan, false)}
                        className={`w-full ${getPlanColor(plan.plan)} hover:opacity-80 text-white py-2 rounded`}
                      >
                        Assinar Mensal
                      </button>
                      {plan.price_yearly > 0 && (
                        <button
                          onClick={() => subscribe(plan.plan, true)}
                          className={`w-full ${getPlanColor(plan.plan)} hover:opacity-80 text-white py-2 rounded border-2 border-white`}
                        >
                          Assinar Anual (Economize!)
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Aba de Afiliados */}
      {activeTab === 'affiliate' && (
        <div className="space-y-6">
          {!isAffiliate ? (
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">Programa de Afiliados</h3>
              <p className="text-gray-300 mb-6">
                Ganhe comissões indicando novos usuários para o GapHunter. 
                Influenciadores recebem 50% de comissão, usuários regulares recebem 30%.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-700 p-4 rounded">
                  <h4 className="font-semibold text-white mb-2">Afiliado Regular</h4>
                  <div className="text-2xl font-bold text-green-400 mb-2">30%</div>
                  <div className="text-sm text-gray-400">de comissão em cada venda</div>
                  <button
                    onClick={() => joinAffiliateProgram(false)}
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
                  >
                    Tornar-se Afiliado
                  </button>
                </div>
                
                <div className="bg-gray-700 p-4 rounded">
                  <h4 className="font-semibold text-white mb-2">Influenciador</h4>
                  <div className="text-2xl font-bold text-yellow-400 mb-2">50%</div>
                  <div className="text-sm text-gray-400">de comissão em cada venda</div>
                  <button
                    onClick={() => joinAffiliateProgram(true)}
                    className="w-full mt-4 bg-yellow-600 hover:bg-yellow-700 text-white py-2 rounded"
                  >
                    Tornar-se Influenciador
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Dashboard do Afiliado */}
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Dashboard do Afiliado</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Ganhos Totais</div>
                    <div className="text-2xl font-bold text-green-400">
                      {formatCurrency(affiliateStats.total_earnings)}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Ganhos Pendentes</div>
                    <div className="text-2xl font-bold text-yellow-400">
                      {formatCurrency(affiliateStats.pending_earnings)}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Total de Indicações</div>
                    <div className="text-2xl font-bold text-white">
                      {affiliateStats.total_referrals}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Taxa de Conversão</div>
                    <div className="text-2xl font-bold text-blue-400">
                      {affiliateStats.conversion_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Link de Afiliado */}
                <div className="bg-gray-700 p-4 rounded mb-6">
                  <h4 className="font-semibold text-white mb-2">Seu Link de Afiliado</h4>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={`https://gaphunter.com?ref=${affiliateStats.affiliate_code}`}
                      readOnly
                      className="flex-1 bg-gray-600 text-white px-3 py-2 rounded border border-gray-500"
                    />
                    <button
                      onClick={() => navigator.clipboard.writeText(`https://gaphunter.com?ref=${affiliateStats.affiliate_code}`)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                    >
                      Copiar
                    </button>
                  </div>
                  <div className="text-sm text-gray-400 mt-2">
                    Código: {affiliateStats.affiliate_code} | Comissão: {affiliateStats.commission_rate}%
                  </div>
                </div>

                {/* Comissões Recentes */}
                {affiliateStats.recent_commissions.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-white mb-3">Comissões Recentes</h4>
                    <div className="space-y-2">
                      {affiliateStats.recent_commissions.slice(0, 5).map((commission) => (
                        <div key={commission.id} className="bg-gray-700 p-3 rounded flex justify-between items-center">
                          <div>
                            <div className="text-white font-medium">
                              {formatCurrency(commission.amount)}
                            </div>
                            <div className="text-sm text-gray-400">
                              {formatDate(commission.earned_date)} - {commission.percentage}%
                            </div>
                          </div>
                          <div className={`px-2 py-1 rounded text-xs ${
                            commission.status === 'paid' ? 'bg-green-600' : 
                            commission.status === 'pending' ? 'bg-yellow-600' : 'bg-gray-600'
                          } text-white`}>
                            {commission.status}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Aba do GapHunter Club */}
      {activeTab === 'club' && (
        <div className="space-y-6">
          {!isClubMember ? (
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">GapHunter Club</h3>
              <p className="text-gray-300 mb-6">
                Junte-se ao clube exclusivo para membros Pro e superiores. 
                Ganhe pontos, desbloqueie benefícios e participe do ranking.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-orange-900 p-4 rounded text-center">
                  <div className="text-orange-400 font-bold text-lg">Bronze</div>
                  <div className="text-sm text-gray-300">0+ pontos</div>
                  <div className="text-sm text-gray-300">0% desconto</div>
                </div>
                <div className="bg-gray-700 p-4 rounded text-center">
                  <div className="text-gray-300 font-bold text-lg">Silver</div>
                  <div className="text-sm text-gray-300">100+ pontos</div>
                  <div className="text-sm text-gray-300">5% desconto</div>
                </div>
                <div className="bg-yellow-900 p-4 rounded text-center">
                  <div className="text-yellow-400 font-bold text-lg">Gold</div>
                  <div className="text-sm text-gray-300">500+ pontos</div>
                  <div className="text-sm text-gray-300">10% desconto</div>
                </div>
                <div className="bg-blue-900 p-4 rounded text-center">
                  <div className="text-blue-400 font-bold text-lg">Diamond</div>
                  <div className="text-sm text-gray-300">1000+ pontos</div>
                  <div className="text-sm text-gray-300">15% desconto</div>
                </div>
              </div>

              <button
                onClick={joinClub}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded text-lg font-semibold"
              >
                Ingressar no GapHunter Club
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Status do Membro */}
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Seu Status no Club</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Nível Atual</div>
                    <div className={`text-2xl font-bold capitalize ${getLevelColor(clubStats.member_level)}`}>
                      {clubStats.member_level}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Pontos</div>
                    <div className="text-2xl font-bold text-white">
                      {clubStats.points}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Desconto</div>
                    <div className="text-2xl font-bold text-green-400">
                      {clubStats.discount_percentage}%
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded">
                    <div className="text-sm text-gray-400">Indicações</div>
                    <div className="text-2xl font-bold text-white">
                      {clubStats.total_referrals}
                    </div>
                  </div>
                </div>

                {/* Progresso para próximo nível */}
                {clubStats.next_level && (
                  <div className="bg-gray-700 p-4 rounded mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white">Progresso para {clubStats.next_level}</span>
                      <span className="text-gray-400">{clubStats.points_to_next_level} pontos restantes</span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{
                          width: `${Math.max(0, 100 - (clubStats.points_to_next_level / 100) * 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Benefícios */}
                <div className="bg-gray-700 p-4 rounded mb-4">
                  <h4 className="font-semibold text-white mb-2">Seus Benefícios</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center">
                      <span className={clubStats.priority_support ? 'text-green-400' : 'text-red-400'}>
                        {clubStats.priority_support ? '✓' : '✗'}
                      </span>
                      <span className="ml-2 text-gray-300">Suporte Prioritário</span>
                    </div>
                    <div className="flex items-center">
                      <span className={clubStats.exclusive_content ? 'text-green-400' : 'text-red-400'}>
                        {clubStats.exclusive_content ? '✓' : '✗'}
                      </span>
                      <span className="ml-2 text-gray-300">Conteúdo Exclusivo</span>
                    </div>
                  </div>
                </div>

                {/* Botão para adicionar pontos (demo) */}
                <button
                  onClick={() => addClubPoints(10)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded"
                >
                  Adicionar 10 Pontos (Demo)
                </button>
              </div>

              {/* Ranking do Club */}
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Ranking do Club</h3>
                <div className="space-y-2">
                  {leaderboard.map((member) => (
                    <div key={member.rank} className="bg-gray-700 p-3 rounded flex justify-between items-center">
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                          member.rank === 1 ? 'bg-yellow-600' :
                          member.rank === 2 ? 'bg-gray-400' :
                          member.rank === 3 ? 'bg-orange-600' : 'bg-gray-600'
                        } text-white`}>
                          {member.rank}
                        </div>
                        <div>
                          <div className="text-white font-medium">{member.username}</div>
                          <div className={`text-sm capitalize ${getLevelColor(member.member_level)}`}>
                            {member.member_level}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-bold">{member.points} pts</div>
                        <div className="text-sm text-gray-400">{member.total_referrals} indicações</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SubscriptionClub;

