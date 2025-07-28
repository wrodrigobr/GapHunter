import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';

const CoachingModule = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isCoach, setIsCoach] = useState(false);
  const [coachProfile, setCoachProfile] = useState(null);
  const [students, setStudents] = useState([]);
  const [availableCoaches, setAvailableCoaches] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentProgress, setStudentProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  const [newCoachProfile, setNewCoachProfile] = useState({
    bio: '',
    specialties: [],
    experience_years: 0,
    hourly_rate: 0,
    max_students: 10
  });

  const [newNote, setNewNote] = useState({
    title: '',
    content: '',
    category: 'general',
    priority: 'medium'
  });

  useEffect(() => {
    loadCoachingData();
  }, []);

  const loadCoachingData = async () => {
    try {
      setLoading(true);
      
      // Tentar carregar perfil de coach
      try {
        const coachResponse = await api.get('/coaching/coach/students');
        setIsCoach(true);
        setStudents(coachResponse.data.students);
      } catch (error) {
        setIsCoach(false);
        // Carregar coaches disponíveis se não for coach
        const coachesResponse = await api.get('/coaching/coaches');
        setAvailableCoaches(coachesResponse.data.coaches);
      }

    } catch (error) {
      console.error('Erro ao carregar dados de coaching:', error);
    } finally {
      setLoading(false);
    }
  };

  const createCoachProfile = async (e) => {
    e.preventDefault();
    try {
      await api.post('/coaching/coach/profile', newCoachProfile);
      setIsCoach(true);
      loadCoachingData();
    } catch (error) {
      console.error('Erro ao criar perfil de coach:', error);
    }
  };

  const loadStudentProgress = async (studentId) => {
    try {
      const response = await api.get(`/coaching/coach/students/${studentId}/progress`);
      setStudentProgress(response.data);
      setSelectedStudent(studentId);
    } catch (error) {
      console.error('Erro ao carregar progresso do aluno:', error);
    }
  };

  const addStudentNote = async (e) => {
    e.preventDefault();
    if (!selectedStudent) return;

    try {
      await api.post('/coaching/coach/notes', {
        ...newNote,
        student_id: selectedStudent
      });
      
      setNewNote({
        title: '',
        content: '',
        category: 'general',
        priority: 'medium'
      });
      
      // Recarregar progresso do aluno
      loadStudentProgress(selectedStudent);
    } catch (error) {
      console.error('Erro ao adicionar nota:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-400',
      high: 'text-orange-400',
      medium: 'text-yellow-400',
      low: 'text-green-400'
    };
    return colors[severity] || 'text-gray-400';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'bg-red-600',
      high: 'bg-orange-600',
      medium: 'bg-yellow-600',
      low: 'bg-green-600'
    };
    return colors[priority] || 'bg-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-white">Carregando módulo de coaching...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Módulo para Coaches</h2>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded ${activeTab === 'overview' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Visão Geral
          </button>
          {isCoach && (
            <>
              <button
                onClick={() => setActiveTab('students')}
                className={`px-4 py-2 rounded ${activeTab === 'students' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
              >
                Meus Alunos
              </button>
              <button
                onClick={() => setActiveTab('progress')}
                className={`px-4 py-2 rounded ${activeTab === 'progress' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
              >
                Progresso
              </button>
            </>
          )}
        </div>
      </div>

      {/* Conteúdo baseado na aba ativa */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {!isCoach ? (
            <div className="space-y-6">
              {/* Formulário para se tornar coach */}
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Torne-se um Coach</h3>
                <form onSubmit={createCoachProfile} className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Bio</label>
                    <textarea
                      value={newCoachProfile.bio}
                      onChange={(e) => setNewCoachProfile({...newCoachProfile, bio: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      rows={3}
                      placeholder="Descreva sua experiência e especialidades..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Anos de Experiência</label>
                      <input
                        type="number"
                        value={newCoachProfile.experience_years}
                        onChange={(e) => setNewCoachProfile({...newCoachProfile, experience_years: parseInt(e.target.value)})}
                        className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Taxa por Hora ($)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={newCoachProfile.hourly_rate}
                        onChange={(e) => setNewCoachProfile({...newCoachProfile, hourly_rate: parseFloat(e.target.value)})}
                        className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Máximo de Alunos</label>
                    <input
                      type="number"
                      value={newCoachProfile.max_students}
                      onChange={(e) => setNewCoachProfile({...newCoachProfile, max_students: parseInt(e.target.value)})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
                  >
                    Criar Perfil de Coach
                  </button>
                </form>
              </div>

              {/* Lista de coaches disponíveis */}
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Coaches Disponíveis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availableCoaches.map((coach) => (
                    <div key={coach.id} className="bg-gray-700 p-4 rounded-lg">
                      <h4 className="font-semibold text-white">{coach.username}</h4>
                      <p className="text-gray-300 text-sm mt-1">{coach.bio}</p>
                      <div className="mt-2 space-y-1">
                        <div className="text-sm text-gray-400">
                          Experiência: {coach.experience_years} anos
                        </div>
                        <div className="text-sm text-gray-400">
                          Taxa: ${coach.hourly_rate}/hora
                        </div>
                        <div className="text-sm text-gray-400">
                          Rating: {coach.rating.toFixed(1)}/5.0 ({coach.total_reviews} avaliações)
                        </div>
                        <div className="text-sm text-gray-400">
                          Vagas: {coach.available_slots}
                        </div>
                      </div>
                      <button className="mt-3 w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded text-sm">
                        Solicitar Coaching
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">Painel do Coach</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-700 p-4 rounded-lg">
                  <h4 className="text-sm text-gray-400">Total de Alunos</h4>
                  <div className="text-2xl font-bold text-white">{students.length}</div>
                </div>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <h4 className="text-sm text-gray-400">Alunos Ativos</h4>
                  <div className="text-2xl font-bold text-white">
                    {students.filter(s => s.recent_hands_count > 0).length}
                  </div>
                </div>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <h4 className="text-sm text-gray-400">Gaps Críticos</h4>
                  <div className="text-2xl font-bold text-red-400">
                    {students.reduce((sum, s) => sum + s.active_gaps, 0)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Aba de Alunos */}
      {activeTab === 'students' && isCoach && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">Meus Alunos</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="text-left py-2">Aluno</th>
                  <th className="text-left py-2">Membro desde</th>
                  <th className="text-right py-2">Mãos Recentes</th>
                  <th className="text-right py-2">Gaps Ativos</th>
                  <th className="text-left py-2">Última Atividade</th>
                  <th className="text-left py-2">Ações</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id} className="border-b border-gray-700">
                    <td className="py-2 text-white">{student.username}</td>
                    <td className="py-2 text-gray-300">{formatDate(student.member_since)}</td>
                    <td className="py-2 text-right text-white">{student.recent_hands_count}</td>
                    <td className="py-2 text-right">
                      <span className={student.active_gaps > 0 ? 'text-red-400' : 'text-green-400'}>
                        {student.active_gaps}
                      </span>
                    </td>
                    <td className="py-2 text-gray-300">
                      {student.last_activity ? formatDate(student.last_activity) : 'N/A'}
                    </td>
                    <td className="py-2">
                      <button
                        onClick={() => loadStudentProgress(student.id)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs"
                      >
                        Ver Progresso
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Aba de Progresso */}
      {activeTab === 'progress' && selectedStudent && studentProgress && (
        <div className="space-y-6">
          {/* Informações do Aluno */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">
              Progresso de {studentProgress.student.username}
            </h3>
            
            {/* Resumo de Gaps */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-700 p-3 rounded">
                <div className="text-sm text-gray-400">Total de Gaps</div>
                <div className="text-xl font-bold text-white">{studentProgress.gaps_summary.total}</div>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <div className="text-sm text-gray-400">Críticos</div>
                <div className="text-xl font-bold text-red-400">{studentProgress.gaps_summary.critical}</div>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <div className="text-sm text-gray-400">Altos</div>
                <div className="text-xl font-bold text-orange-400">{studentProgress.gaps_summary.high}</div>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <div className="text-sm text-gray-400">Mãos Recentes</div>
                <div className="text-xl font-bold text-white">{studentProgress.recent_activity.hands_count}</div>
              </div>
            </div>

            {/* Lista de Gaps */}
            <div className="mb-6">
              <h4 className="text-md font-semibold text-white mb-3">Gaps Identificados</h4>
              <div className="space-y-2">
                {studentProgress.gaps_detail.slice(0, 5).map((gap) => (
                  <div key={gap.id} className="bg-gray-700 p-3 rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium text-white">{gap.type}</div>
                        <div className="text-sm text-gray-300">{gap.description}</div>
                        <div className="text-xs text-blue-400 mt-1">{gap.suggestion}</div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${getSeverityColor(gap.severity)}`}>
                          {gap.severity}
                        </div>
                        <div className="text-xs text-gray-400">
                          Freq: {gap.frequency}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Adicionar Nota */}
            <div className="bg-gray-700 p-4 rounded">
              <h4 className="text-md font-semibold text-white mb-3">Adicionar Nota</h4>
              <form onSubmit={addStudentNote} className="space-y-3">
                <div>
                  <input
                    type="text"
                    placeholder="Título da nota"
                    value={newNote.title}
                    onChange={(e) => setNewNote({...newNote, title: e.target.value})}
                    className="w-full bg-gray-600 text-white px-3 py-2 rounded border border-gray-500"
                    required
                  />
                </div>
                <div>
                  <textarea
                    placeholder="Conteúdo da nota"
                    value={newNote.content}
                    onChange={(e) => setNewNote({...newNote, content: e.target.value})}
                    className="w-full bg-gray-600 text-white px-3 py-2 rounded border border-gray-500"
                    rows={3}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <select
                    value={newNote.category}
                    onChange={(e) => setNewNote({...newNote, category: e.target.value})}
                    className="bg-gray-600 text-white px-3 py-2 rounded border border-gray-500"
                  >
                    <option value="general">Geral</option>
                    <option value="gap">Gap</option>
                    <option value="improvement">Melhoria</option>
                    <option value="homework">Tarefa</option>
                  </select>
                  <select
                    value={newNote.priority}
                    onChange={(e) => setNewNote({...newNote, priority: e.target.value})}
                    className="bg-gray-600 text-white px-3 py-2 rounded border border-gray-500"
                  >
                    <option value="low">Baixa</option>
                    <option value="medium">Média</option>
                    <option value="high">Alta</option>
                    <option value="critical">Crítica</option>
                  </select>
                </div>
                <button
                  type="submit"
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded"
                >
                  Adicionar Nota
                </button>
              </form>
            </div>

            {/* Notas Existentes */}
            {studentProgress.coach_notes.length > 0 && (
              <div className="mt-6">
                <h4 className="text-md font-semibold text-white mb-3">Notas do Coach</h4>
                <div className="space-y-2">
                  {studentProgress.coach_notes.slice(0, 5).map((note) => (
                    <div key={note.id} className="bg-gray-700 p-3 rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-white">{note.title}</div>
                          <div className="text-sm text-gray-300">{note.content}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {formatDate(note.created_at)} - {note.category}
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs text-white ${getPriorityColor(note.priority)}`}>
                          {note.priority}
                        </div>
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
  );
};

export default CoachingModule;

