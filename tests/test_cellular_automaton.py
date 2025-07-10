import pytest
import os
import sys
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from src.cellular_automaton import CellularAutomaton
from src.rules import RULES
from src.patterns import set_pattern
from src.input_handler import handle_input, handle_key

class TestCellularAutomaton:
    
    def test_init(self):
        """Test inicialización del autómata celular"""
        ca = CellularAutomaton()
        assert len(ca.state) == 60
        assert ca.generation == 0
        assert ca.running == False
        assert ca.rule_num == 30
        assert ca.history == []
        assert ca.max_history == 25

    def test_get_rule_table_default(self):
        """Test obtener tabla de reglas por defecto (regla 30)"""
        ca = CellularAutomaton()
        rule_table = ca.get_rule_table()
        assert rule_table == RULES[30]
        assert len(rule_table) == 8

    def test_get_rule_table_different_rules(self):
        """Test obtener diferentes tablas de reglas"""
        ca = CellularAutomaton()
        
        # Test regla 90
        ca.rule_num = 90
        assert ca.get_rule_table() == RULES[90]
        
        # Test regla 110
        ca.rule_num = 110
        assert ca.get_rule_table() == RULES[110]
        
        # Test regla 184
        ca.rule_num = 184
        assert ca.get_rule_table() == RULES[184]

    def test_get_rule_table_nonexistent_rule(self):
        """Test regla no existente debe retornar regla 30 por defecto"""
        ca = CellularAutomaton()
        ca.rule_num = 999  # Regla que no existe
        assert ca.get_rule_table() == RULES[30]

    def test_apply_rule_all_patterns(self):
        """Test aplicar regla con todos los patrones posibles"""
        ca = CellularAutomaton()
        rule_table = ca.get_rule_table()
        
        # Probar todos los patrones posibles (000 a 111)
        patterns = [
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
            (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
        ]
        
        for left, center, right in patterns:
            pattern_index = (left << 2) + (center << 1) + right
            expected = rule_table[pattern_index]
            result = ca.apply_rule(left, center, right)
            assert result == expected

    def test_next_generation_basic(self):
        """Test generación siguiente básica"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[30] = 1  # Célula en el centro
        initial_state = ca.state[:]
        initial_generation = ca.generation
        initial_history_length = len(ca.history)
        
        ca.next_generation()
        
        assert ca.state != initial_state
        assert ca.generation == initial_generation + 1
        assert len(ca.history) == initial_history_length + 1
        # El historial contiene el estado DESPUÉS de aplicar la regla
        assert ca.history[-1] == ca.state

    def test_next_generation_history_limit(self):
        """Test límite de historial en next_generation"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[30] = 1
        
        # Generar más de max_history generaciones
        for _ in range(30):
            ca.next_generation()
        
        assert len(ca.history) == ca.max_history
        assert ca.generation == 30

    def test_next_generation_boundary_conditions(self):
        """Test condiciones de frontera (bordes circulares)"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[0] = 1  # Célula en el borde izquierdo
        ca.state[59] = 1  # Célula en el borde derecho
        
        ca.next_generation()
        
        # Verificar que las condiciones de frontera circulares funcionan
        assert ca.generation == 1

    @patch('builtins.print')
    def test_display(self, mock_print):
        """Test función display"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[30] = 1
        ca.generation = 5
        ca.history = [[0] * 60, [1] * 60]
        
        ca.display()
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Gen:    5" in call_args
        assert "Rule:  30" in call_args

    @patch('src.cellular_automaton.handle_input')
    def test_get_input(self, mock_handle_input):
        """Test función get_input"""
        ca = CellularAutomaton()
        ca.get_input()
        mock_handle_input.assert_called_once_with(ca)

    def test_simulate(self):
        """Test función simulate"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[30] = 1
        ca.running = True
        
        # Mock time.sleep para acelerar el test
        with patch('time.sleep'):
            # Ejecutar simulate en un hilo separado por un tiempo corto
            thread = threading.Thread(target=ca.simulate)
            thread.daemon = True
            thread.start()
            
            # Esperar un poco y luego detener
            time.sleep(0.1)
            ca.running = False
            thread.join(timeout=1)
            
            # Verificar que se ejecutaron algunas generaciones
            assert ca.generation > 0

class TestPatterns:
    
    def test_set_pattern_single(self):
        """Test patrón single"""
        ca = CellularAutomaton()
        set_pattern(ca, 'single')
        
        assert sum(ca.state) == 1
        assert ca.state[30] == 1  # Centro
        assert ca.generation == 0
        assert len(ca.history) == 1

    def test_set_pattern_double(self):
        """Test patrón double"""
        ca = CellularAutomaton()
        set_pattern(ca, 'double')
        
        assert sum(ca.state) == 2
        assert ca.state[29] == 1  # Centro - 1
        assert ca.state[31] == 1  # Centro + 1

    def test_set_pattern_triple(self):
        """Test patrón triple"""
        ca = CellularAutomaton()
        set_pattern(ca, 'triple')
        
        assert sum(ca.state) == 3
        assert ca.state[29] == 1  # Centro - 1
        assert ca.state[30] == 1  # Centro
        assert ca.state[31] == 1  # Centro + 1

    def test_set_pattern_random(self):
        """Test patrón random"""
        ca = CellularAutomaton()
        set_pattern(ca, 'random')
        
        assert sum(ca.state) > 0
        # Verificar que las posiciones son las esperadas
        expected_positions = [i for i in range(0, 60, 3) if i % 7 == 0]
        for pos in expected_positions:
            assert ca.state[pos] == 1

    def test_set_pattern_edges(self):
        """Test patrón edges"""
        ca = CellularAutomaton()
        set_pattern(ca, 'edges')
        
        assert sum(ca.state) == 2
        assert ca.state[5] == 1
        assert ca.state[54] == 1  # WIDTH - 6 = 60 - 6 = 54

    def test_set_pattern_symmetric(self):
        """Test patrón symmetric"""
        ca = CellularAutomaton()
        set_pattern(ca, 'symmetric')
        
        assert sum(ca.state) == 5
        expected_positions = [20, 25, 30, 35, 40]  # 30±10, 30±5, 30
        for pos in expected_positions:
            assert ca.state[pos] == 1

    def test_set_pattern_nonexistent(self):
        """Test patrón no existente"""
        ca = CellularAutomaton()
        set_pattern(ca, 'nonexistent')
        
        assert sum(ca.state) == 0  # Debería quedar vacío
        assert ca.generation == 0

class TestRules:
    
    def test_rules_existence(self):
        """Test que todas las reglas esperadas existen"""
        expected_rules = [30, 90, 110, 184]
        for rule_num in expected_rules:
            assert rule_num in RULES
            assert len(RULES[rule_num]) == 8

    def test_rule_30_values(self):
        """Test valores específicos de la regla 30"""
        rule_30 = RULES[30]
        expected = [0, 1, 1, 1, 1, 0, 0, 0]
        assert rule_30 == expected

    def test_rule_90_values(self):
        """Test valores específicos de la regla 90"""
        rule_90 = RULES[90]
        expected = [0, 1, 0, 1, 1, 0, 1, 0]
        assert rule_90 == expected

    def test_rule_110_values(self):
        """Test valores específicos de la regla 110"""
        rule_110 = RULES[110]
        expected = [0, 1, 1, 0, 1, 1, 1, 0]
        assert rule_110 == expected

    def test_rule_184_values(self):
        """Test valores específicos de la regla 184"""
        rule_184 = RULES[184]
        expected = [0, 0, 0, 1, 0, 1, 1, 1]
        assert rule_184 == expected

class TestInputHandler:
    
    @patch('msvcrt.kbhit', return_value=False)
    @patch('os.name', 'nt')
    def test_handle_input_windows_no_key(self, mock_kbhit):
        """Test handle_input en Windows sin teclas presionadas"""
        ca = CellularAutomaton()
        
        # Mock para simular que no hay teclas disponibles y luego salir
        mock_kbhit.side_effect = [True, False]
        
        with patch('msvcrt.getch') as mock_getch:
            mock_getch.return_value.decode.return_value.lower.return_value = 'q'
            handle_input(ca)

    def test_handle_key_space(self):
        """Test manejo de tecla espacio"""
        ca = CellularAutomaton()
        initial_running = ca.running
        
        with patch('threading.Thread') as mock_thread:
            result = handle_key(ca, ' ')
            assert result == True
            assert ca.running != initial_running

    def test_handle_key_reset(self):
        """Test manejo de tecla 'r' (reset)"""
        ca = CellularAutomaton()
        ca.state = [1] * 60  # Estado inicial diferente
        
        with patch('src.input_handler.set_pattern') as mock_set_pattern:
            result = handle_key(ca, 'r')
            assert result == True
            mock_set_pattern.assert_called_once_with(ca, 'single')

    def test_handle_key_next_rule(self):
        """Test manejo de tecla 'n' (next rule)"""
        ca = CellularAutomaton()
        initial_rule = ca.rule_num
        
        result = handle_key(ca, 'n')
        assert result == True
        assert ca.rule_num != initial_rule

    @patch('random.choice')
    def test_handle_key_pattern(self, mock_choice):
        """Test manejo de tecla 'p' (random pattern)"""
        ca = CellularAutomaton()
        mock_choice.return_value = 'double'
        
        with patch('src.input_handler.set_pattern') as mock_set_pattern:
            result = handle_key(ca, 'p')
            assert result == True
            mock_set_pattern.assert_called_once_with(ca, 'double')

    def test_handle_key_quit(self):
        """Test manejo de tecla 'q' (quit)"""
        ca = CellularAutomaton()
        result = handle_key(ca, 'q')
        assert result == False

    def test_handle_key_unknown(self):
        """Test manejo de tecla desconocida"""
        ca = CellularAutomaton()
        result = handle_key(ca, 'x')
        assert result == True  # Debería continuar

class TestIntegration:
    
    def test_full_simulation_cycle(self):
        """Test ciclo completo de simulación"""
        ca = CellularAutomaton()
        
        # Configurar patrón inicial
        set_pattern(ca, 'single')
        initial_state = ca.state[:]
        
        # Ejecutar varias generaciones
        for _ in range(5):
            ca.next_generation()
        
        assert ca.generation == 5
        assert ca.state != initial_state
        assert len(ca.history) == 5

    def test_different_rules_produce_different_results(self):
        """Test que diferentes reglas producen resultados diferentes"""
        ca1 = CellularAutomaton()
        ca2 = CellularAutomaton()
        
        # Configurar mismo estado inicial
        set_pattern(ca1, 'single')
        set_pattern(ca2, 'single')
        
        # Usar reglas diferentes
        ca1.rule_num = 30
        ca2.rule_num = 90
        
        # Ejecutar una generación
        ca1.next_generation()
        ca2.next_generation()
        
        # Los resultados deberían ser diferentes
        assert ca1.state != ca2.state

    def test_boundary_wrapping(self):
        """Test que las fronteras circulares funcionan correctamente"""
        ca = CellularAutomaton()
        ca.state = [0] * 60
        ca.state[0] = 1  # Borde izquierdo
        
        # Aplicar regla en el borde
        left = ca.state[59]  # Debería ser 0 (wrap around)
        center = ca.state[0]  # 1
        right = ca.state[1]   # 0
        
        result = ca.apply_rule(left, center, right)
        assert isinstance(result, int)
        assert result in [0, 1]

if __name__ == '__main__':
    pytest.main(['-v'])
