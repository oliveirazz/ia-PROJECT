from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import csv
from datetime import datetime

class SistemaAlocacao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciamento de Professores e Disciplinas")
        self.setGeometry(100, 100, 1200, 800)
        
        # Listas para armazenar dados
        self.professores = []
        self.disciplinas = []
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout(self.central_widget)
        
        # Barra de ferramentas
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Botões da barra de ferramentas
        btn_alocar = QPushButton("Alocar Professores")
        btn_export_json = QPushButton("Exportar para JSON")
        btn_export_csv = QPushButton("Exportar para CSV")
        
        toolbar.addWidget(btn_alocar)
        toolbar.addWidget(btn_export_json)
        toolbar.addWidget(btn_export_csv)
        
        # Seção de Cadastro de Professor
        grupo_prof = QGroupBox("Cadastrar Professor")
        layout_prof = QHBoxLayout()
        
        # Campos de entrada para professor
        self.nome_prof = QLineEdit()
        self.area_prof = QComboBox()
        self.area_prof.addItems(["Desenvolvimento", "Infraestrutura", "Desenvolvimento e Infraestrutura", "Outros"])
        self.modalidade_prof = QComboBox()
        self.modalidade_prof.addItems(["Presencial", "EAD", "Híbrido"])
        
        layout_prof.addWidget(QLabel("Nome:"))
        layout_prof.addWidget(self.nome_prof)
        layout_prof.addWidget(QLabel("Área:"))
        layout_prof.addWidget(self.area_prof)
        layout_prof.addWidget(QLabel("Modalidade:"))
        layout_prof.addWidget(self.modalidade_prof)
        
        # Grupo de disponibilidade
        grupo_disp = QGroupBox("Disponibilidade")
        layout_disp = QGridLayout()
        
        # Dias da semana
        self.dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        # Períodos
        self.periodos = ["Manhã", "Tarde", "Noite"]
        
        # Criar checkboxes para cada combinação de dia e período
        self.check_disponibilidade = {}
        
        # Adicionar labels
        for col, dia in enumerate(self.dias):
            layout_disp.addWidget(QLabel(dia), 0, col + 1)
        for row, periodo in enumerate(self.periodos):
            layout_disp.addWidget(QLabel(periodo), row + 1, 0)
        
        # Adicionar checkboxes
        for row, periodo in enumerate(self.periodos):
            for col, dia in enumerate(self.dias):
                checkbox = QCheckBox()
                self.check_disponibilidade[f"{dia} {periodo}"] = checkbox
                layout_disp.addWidget(checkbox, row + 1, col + 1)
        
        grupo_disp.setLayout(layout_disp)
        layout_prof.addWidget(grupo_disp)
        
        # Adicionar botão de cadastrar professor
        btn_cadastrar_prof = QPushButton("Cadastrar")
        layout_prof.addWidget(btn_cadastrar_prof)
        
        grupo_prof.setLayout(layout_prof)
        
        # Tabela de Professores
        self.tabela_prof = QTableWidget()
        self.tabela_prof.setColumnCount(4)
        self.tabela_prof.setHorizontalHeaderLabels(["Nome", "Área", "Disponibilidade", "Modalidade"])
        self.tabela_prof.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Botão Excluir Professor
        btn_excluir_prof = QPushButton("Excluir Professor")
        
        # Seção de Cadastro de Disciplina
        grupo_disc = QGroupBox("Cadastrar Disciplina")
        layout_disc = QHBoxLayout()
        
        # Campos de entrada para disciplina
        self.nome_disc = QLineEdit()
        self.tipo_disc = QComboBox()
        self.tipo_disc.addItems(["Teórica", "Prática", "Teórica/Prática"])
        self.lab_check = QCheckBox("Necessita Lab?")
        self.predio_disc = QComboBox()
        self.predio_disc.addItems([
            "Prédio 1",
            "Prédio 2",
            "Prédio 3",
            "Laboratório de elétrica / eletrônica"
        ])
        self.sala_disc = QComboBox()
        
        # Atualizar salas quando prédio for selecionado
        self.predio_disc.currentTextChanged.connect(self.atualizar_salas)
        
        layout_disc.addWidget(QLabel("Nome:"))
        layout_disc.addWidget(self.nome_disc)
        layout_disc.addWidget(QLabel("Tipo:"))
        layout_disc.addWidget(self.tipo_disc)
        layout_disc.addWidget(self.lab_check)
        layout_disc.addWidget(QLabel("Prédio:"))
        layout_disc.addWidget(self.predio_disc)
        layout_disc.addWidget(QLabel("Sala:"))
        layout_disc.addWidget(self.sala_disc)
        
        # Grupo de horário da disciplina
        grupo_horario = QGroupBox("Horário")
        layout_horario = QGridLayout()
        
        # Usar os mesmos dias e períodos definidos anteriormente
        # Criar checkboxes para cada combinação de dia e período
        self.check_horario_disc = {}
        
        # Adicionar labels
        for col, dia in enumerate(self.dias):
            layout_horario.addWidget(QLabel(dia), 0, col + 1)
        for row, periodo in enumerate(self.periodos):
            layout_horario.addWidget(QLabel(periodo), row + 1, 0)
        
        # Adicionar checkboxes (apenas um pode ser selecionado)
        for row, periodo in enumerate(self.periodos):
            for col, dia in enumerate(self.dias):
                checkbox = QCheckBox()
                checkbox.clicked.connect(lambda checked, r=row, c=col: self.horario_selecionado(r, c))
                self.check_horario_disc[f"{dia} {periodo}"] = checkbox
                layout_horario.addWidget(checkbox, row + 1, col + 1)
        
        grupo_horario.setLayout(layout_horario)
        layout_disc.addWidget(grupo_horario)
        
        # Botão cadastrar
        btn_cadastrar_disc = QPushButton("Cadastrar")
        layout_disc.addWidget(btn_cadastrar_disc)
        
        grupo_disc.setLayout(layout_disc)
        
        # Tabela de Disciplinas
        self.tabela_disc = QTableWidget()
        self.tabela_disc.setColumnCount(6)
        self.tabela_disc.setHorizontalHeaderLabels([
            "Nome", 
            "Tipo", 
            "Laboratório", 
            "Horário", 
            "Professor",
            "Local"
        ])
        self.tabela_disc.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Botão Excluir Disciplina
        btn_excluir_disc = QPushButton("Excluir Disciplina")
        
        # Adicionar widgets ao layout principal
        self.layout_principal.addWidget(grupo_prof)
        self.layout_principal.addWidget(self.tabela_prof)
        self.layout_principal.addWidget(btn_excluir_prof)
        self.layout_principal.addWidget(grupo_disc)
        self.layout_principal.addWidget(self.tabela_disc)
        self.layout_principal.addWidget(btn_excluir_disc)
        
        # Conectar sinais
        btn_cadastrar_prof.clicked.connect(self.cadastrar_professor)
        btn_cadastrar_disc.clicked.connect(self.cadastrar_disciplina)
        btn_excluir_prof.clicked.connect(self.excluir_professor)
        btn_excluir_disc.clicked.connect(self.excluir_disciplina)
        btn_alocar.clicked.connect(self.alocar_professores_automaticamente)
        btn_export_json.clicked.connect(self.exportar_json)
        btn_export_csv.clicked.connect(self.exportar_csv)
        
        # Conectar evento de seleção do prédio
        self.predio_disc.currentTextChanged.connect(self.atualizar_salas)

    def horario_selecionado(self, row, col):
        # Desmarcar todos os outros checkboxes
        for r, periodo in enumerate(self.periodos):
            for c, dia in enumerate(self.dias):
                if r != row or c != col:
                    self.check_horario_disc[f"{dia} {periodo}"].setChecked(False)

    def cadastrar_professor(self):
        nome = self.nome_prof.text()
        area = self.area_prof.currentText()
        modalidade = self.modalidade_prof.currentText()
        
        # Coletar disponibilidade
        disponibilidade = []
        for chave, checkbox in self.check_disponibilidade.items():
            if checkbox.isChecked():
                disponibilidade.append(chave)
        
        # Validação
        if not nome:
            QMessageBox.warning(self, "Erro", "O nome do professor é obrigatório!")
            return
        if not disponibilidade:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos um horário de disponibilidade!")
            return
        
        # Criar professor
        professor = {
            "nome": nome,
            "area": area,
            "disponibilidade": disponibilidade,
            "modalidade": modalidade
        }
        
        self.professores.append(professor)
        self.atualizar_tabela_professores()
        self.limpar_campos_professor()
        QMessageBox.information(self, "Sucesso", "Professor cadastrado com sucesso!")

    def excluir_professor(self):
        linha_selecionada = self.tabela_prof.currentRow()
        if linha_selecionada >= 0:
            nome_professor = self.tabela_prof.item(linha_selecionada, 0).text()
            resposta = QMessageBox.question(self, "Confirmar Exclusão", 
                                          f"Deseja excluir o professor {nome_professor}?",
                                          QMessageBox.Yes | QMessageBox.No)
            
            if resposta == QMessageBox.Yes:
                self.professores.pop(linha_selecionada)
                self.atualizar_tabela_professores()
                QMessageBox.information(self, "Sucesso", "Professor excluído com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Selecione um professor para excluir!")

    def cadastrar_disciplina(self):
        nome = self.nome_disc.text()
        tipo = self.tipo_disc.currentText()
        necessita_lab = "Sim" if self.lab_check.isChecked() else "Não"
        predio = self.predio_disc.currentText()
        sala = self.sala_disc.currentText()
        
        # Coletar horário
        horario = None
        for chave, checkbox in self.check_horario_disc.items():
            if checkbox.isChecked():
                horario = chave
                break
        
        # Validação
        if not nome:
            QMessageBox.warning(self, "Erro", "O nome da disciplina é obrigatório!")
            return
        if not horario:
            QMessageBox.warning(self, "Erro", "Selecione um horário para a disciplina!")
            return
        
        # Criar disciplina
        disciplina = {
            "nome": nome,
            "tipo": tipo,
            "necessita_lab": necessita_lab,
            "horario": horario,
            "professor": "Não alocado",
            "predio": predio,
            "sala": sala
        }
        
        self.disciplinas.append(disciplina)
        self.atualizar_tabela_disciplinas()
        self.limpar_campos_disciplina()
        QMessageBox.information(self, "Sucesso", "Disciplina cadastrada com sucesso!")

    def excluir_disciplina(self):
        linha_selecionada = self.tabela_disc.currentRow()
        if linha_selecionada >= 0:
            nome_disciplina = self.tabela_disc.item(linha_selecionada, 0).text()
            resposta = QMessageBox.question(self, "Confirmar Exclusão", 
                                          f"Deseja excluir a disciplina {nome_disciplina}?",
                                          QMessageBox.Yes | QMessageBox.No)
            
            if resposta == QMessageBox.Yes:
                self.disciplinas.pop(linha_selecionada)
                self.atualizar_tabela_disciplinas()
                QMessageBox.information(self, "Sucesso", "Disciplina excluída com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Selecione uma disciplina para excluir!")

    def atualizar_tabela_professores(self):
        self.tabela_prof.setRowCount(0)
        for professor in self.professores:
            row = self.tabela_prof.rowCount()
            self.tabela_prof.insertRow(row)
            self.tabela_prof.setItem(row, 0, QTableWidgetItem(professor["nome"]))
            self.tabela_prof.setItem(row, 1, QTableWidgetItem(professor["area"]))
            self.tabela_prof.setItem(row, 2, QTableWidgetItem(", ".join(professor["disponibilidade"])))
            self.tabela_prof.setItem(row, 3, QTableWidgetItem(professor["modalidade"]))

    def atualizar_tabela_disciplinas(self):
        self.tabela_disc.setRowCount(0)
        for disciplina in self.disciplinas:
            row = self.tabela_disc.rowCount()
            self.tabela_disc.insertRow(row)
            self.tabela_disc.setItem(row, 0, QTableWidgetItem(disciplina["nome"]))
            self.tabela_disc.setItem(row, 1, QTableWidgetItem(disciplina["tipo"]))
            self.tabela_disc.setItem(row, 2, QTableWidgetItem(disciplina["necessita_lab"]))
            self.tabela_disc.setItem(row, 3, QTableWidgetItem(disciplina["horario"]))
            self.tabela_disc.setItem(row, 4, QTableWidgetItem(disciplina["professor"]))
            self.tabela_disc.setItem(row, 5, QTableWidgetItem(f"{disciplina['predio']} - Sala {disciplina['sala']}"))

    def limpar_campos_professor(self):
        self.nome_prof.clear()
        self.area_prof.setCurrentIndex(0)
        self.modalidade_prof.setCurrentIndex(0)
        for checkbox in self.check_disponibilidade.values():
            checkbox.setChecked(False)

    def limpar_campos_disciplina(self):
        self.nome_disc.clear()
        self.tipo_disc.setCurrentIndex(0)
        self.lab_check.setChecked(False)
        self.predio_disc.setCurrentIndex(0)
        self.sala_disc.setCurrentIndex(0)
        for checkbox in self.check_horario_disc.values():
            checkbox.setChecked(False)

    def calcular_compatibilidade_alocacao(self, professor, disciplina):
        pontuacao = 0
        areas_prof = professor["area"].split(" e ")

        # Verificar modalidade primeiro (critério eliminatório)
        if disciplina["modalidade"] == "EAD" and "EAD" not in professor["modalidade"]:
            return 0
        if disciplina["modalidade"] == "Presencial" and "Presencial" not in professor["modalidade"]:
            return 0
        if disciplina["modalidade"] == "Híbrido" and "Híbrido" not in professor["modalidade"]:
            return 0

        # Professores compartilhados (outras áreas) têm prioridade em suas disciplinas específicas
        if "Outros" in areas_prof and disciplina["tipo"] == "Teórica":
            pontuacao += 5  # Maior pontuação para garantir a alocação
            return pontuacao

        # Verificar área de atuação
        if disciplina["tipo"] in ["Prática", "Teórica/Prática"]:
            if "Desenvolvimento" in areas_prof and disciplina["area"] == "Desenvolvimento":
                pontuacao += 4
            elif "Infraestrutura" in areas_prof and disciplina["area"] == "Infraestrutura":
                pontuacao += 4
            elif "Desenvolvimento e Infraestrutura" in areas_prof:
                pontuacao += 3
        else:  # Disciplinas teóricas
            if "Desenvolvimento e Infraestrutura" in areas_prof:
                pontuacao += 2
            elif "Desenvolvimento" in areas_prof or "Infraestrutura" in areas_prof:
                pontuacao += 1

        # Bônus para professores com mais modalidades (mais flexíveis)
        pontuacao += len(professor["modalidade"]) * 0.5

        # Verificar carga atual do professor
        aulas_alocadas = len([d for d in self.disciplinas if d["professor"] == professor["nome"]])
        if aulas_alocadas < 2:
            pontuacao += 2  # Priorizar professores com menos de 2 aulas
        elif aulas_alocadas >= 6:
            return 0  # Professor já está com carga máxima

        return pontuacao

    def alocar_professores_automaticamente(self):
        try:
            if not self.professores or not self.disciplinas:
                QMessageBox.warning(self, "Erro", "É necessário ter professores e disciplinas cadastrados!")
                return

            # Resetar alocações anteriores
            for disciplina in self.disciplinas:
                disciplina["professor"] = "Não alocado"

            # Ordenar disciplinas por prioridade
            disciplinas_ordenadas = sorted(self.disciplinas, 
                key=lambda d: (
                    d.get("modalidade", "") == "EAD",     
                    d.get("necessita_lab", "") == "Sim",  
                    d.get("tipo", "") == "Prática",       
                    d.get("tipo", "") == "Teórica/Prática"
                ), 
                reverse=True
            )

            # Alocações por modalidade
            for modalidade in ["EAD", "Híbrido", "Presencial"]:
                # Filtrar disciplinas da modalidade atual
                disc_modalidade = [d for d in disciplinas_ordenadas 
                                if d.get("modalidade", "") == modalidade and 
                                d.get("professor", "") == "Não alocado"]
                
                # Filtrar professores que podem dar aula nesta modalidade
                prof_modalidade = [p for p in self.professores 
                                if modalidade in p.get("modalidade", [])]
                
                for disciplina in disc_modalidade:
                    melhor_professor = None
                    maior_pontuacao = -1

                    for professor in prof_modalidade:
                        # Verificar conflitos de horário
                        tem_conflito = False
                        for d in self.disciplinas:
                            if (d.get("professor", "") == professor.get("nome", "") and 
                                d.get("horario", "") == disciplina.get("horario", "")):
                                tem_conflito = True
                                break
                        
                        if tem_conflito:
                            continue

                        # Verificar disponibilidade
                        if disciplina.get("horario", "") not in professor.get("disponibilidade", []):
                            continue

                        # Calcular pontuação
                        try:
                            pontuacao = self.calcular_compatibilidade_alocacao(professor, disciplina)
                        except Exception as e:
                            print(f"Erro ao calcular compatibilidade: {e}")
                            continue
                        
                        if pontuacao > maior_pontuacao:
                            melhor_professor = professor
                            maior_pontuacao = pontuacao

                    if melhor_professor and maior_pontuacao > 0:
                        disciplina["professor"] = melhor_professor["nome"]

            self.mostrar_resultado_alocacao_detalhado()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante a alocação: {str(e)}")
            print(f"Erro detalhado: {e}")

    def mostrar_resultado_alocacao_detalhado(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Resultado da Alocação")
            dialog.setGeometry(100, 100, 1000, 700)
            layout = QVBoxLayout()

            # Tabela de resultados
            tabela = QTableWidget()
            tabela.setColumnCount(8)
            tabela.setHorizontalHeaderLabels([
                "Disciplina", 
                "Professor", 
                "Área Prof.",
                "Modalidade",
                "Horário",
                "Tipo",
                "Local",
                "Status"
            ])

            # Preencher tabela
            for disciplina in self.disciplinas:
                row = tabela.rowCount()
                tabela.insertRow(row)
                
                # Buscar área do professor
                area_prof = "N/A"
                for prof in self.professores:
                    if prof.get("nome", "") == disciplina.get("professor", ""):
                        area_prof = prof.get("area", "N/A")
                        break
                
                tabela.setItem(row, 0, QTableWidgetItem(str(disciplina.get("nome", ""))))
                tabela.setItem(row, 1, QTableWidgetItem(str(disciplina.get("professor", ""))))
                tabela.setItem(row, 2, QTableWidgetItem(str(area_prof)))
                tabela.setItem(row, 3, QTableWidgetItem(str(disciplina.get("modalidade", ""))))
                tabela.setItem(row, 4, QTableWidgetItem(str(disciplina.get("horario", ""))))
                tabela.setItem(row, 5, QTableWidgetItem(str(disciplina.get("tipo", ""))))
                tabela.setItem(row, 6, QTableWidgetItem(
                    f"{disciplina.get('predio', '')} - Sala {disciplina.get('sala', '')}"
                ))
                
                status = "Alocado" if disciplina.get("professor", "") != "Não alocado" else "Não alocado"
                tabela.setItem(row, 7, QTableWidgetItem(status))

                # Colorir linha baseado no status
                cor = QColor(200, 255, 200) if status == "Alocado" else QColor(255, 200, 200)
                for col in range(tabela.columnCount()):
                    tabela.item(row, col).setBackground(cor)

            tabela.resizeColumnsToContents()
            layout.addWidget(tabela)

            # Estatísticas detalhadas
            total_disc = len(self.disciplinas)
            alocadas = len([d for d in self.disciplinas if d.get("professor", "") != "Não alocado"])
            
            stats = QLabel(f"""
            Estatísticas da Alocação:
            - Total de disciplinas: {total_disc}
            - Disciplinas alocadas: {alocadas}
            - Disciplinas não alocadas: {total_disc - alocadas}
            - Taxa de sucesso: {(alocadas/total_disc)*100:.1f}%
            
            Por Modalidade:
            - EAD: {len([d for d in self.disciplinas if d.get('modalidade', '') == 'EAD' and d.get('professor', '') != 'Não alocado'])}
            - Híbrido: {len([d for d in self.disciplinas if d.get('modalidade', '') == 'Híbrido' and d.get('professor', '') != 'Não alocado'])}
            - Presencial: {len([d for d in self.disciplinas if d.get('modalidade', '') == 'Presencial' and d.get('professor', '') != 'Não alocado'])}
            """)
            layout.addWidget(stats)

            # Botões
            botoes = QHBoxLayout()
            btn_confirmar = QPushButton("Confirmar Alocação")
            btn_tentar_novamente = QPushButton("Tentar Novamente")
            btn_cancelar = QPushButton("Cancelar")

            btn_confirmar.clicked.connect(dialog.accept)
            btn_tentar_novamente.clicked.connect(lambda: (dialog.reject(), self.alocar_professores_automaticamente()))
            btn_cancelar.clicked.connect(dialog.reject)

            botoes.addWidget(btn_confirmar)
            botoes.addWidget(btn_tentar_novamente)
            botoes.addWidget(btn_cancelar)
            layout.addLayout(botoes)

            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao mostrar o resultado: {str(e)}")
            print(f"Erro detalhado: {e}")

    def exportar_json(self):
        dados = {
            "professores": self.professores,
            "disciplinas": self.disciplinas
        }
        nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Exportar JSON", "", "JSON (*.json)")
        if nome_arquivo:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Sucesso", "Dados exportados com sucesso!")

    def exportar_csv(self):
        nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "", "CSV (*.csv)")
        if nome_arquivo:
            with open(nome_arquivo, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                # Exportar professores
                writer.writerow(["PROFESSORES"])
                writer.writerow(["Nome", "Área", "Disponibilidade", "Modalidade"])
                for prof in self.professores:
                    writer.writerow([
                        prof["nome"],
                        prof["area"],
                        ", ".join(prof["disponibilidade"]),
                        prof["modalidade"]
                    ])
                # Exportar disciplinas
                writer.writerow([])
                writer.writerow(["DISCIPLINAS"])
                writer.writerow(["Nome", "Tipo", "Laboratório", "Horário", "Professor", "Local"])
                for disc in self.disciplinas:
                    writer.writerow([
                        disc["nome"],
                        disc["tipo"],
                        disc["necessita_lab"],
                        disc["horario"],
                        disc["professor"],
                        f"{disc['predio']} - Sala {disc['sala']}"
                    ])
            QMessageBox.information(self, "Sucesso", "Dados exportados com sucesso!")

    def atualizar_salas(self, predio):
        self.sala_disc.clear()
        if predio == "Prédio 1":
            self.sala_disc.addItems(["101", "102", "103", "104", "105"])
        elif predio == "Prédio 2":
            self.sala_disc.addItems(["201", "202", "203", "204", "205"])
        elif predio == "Prédio 3":
            self.sala_disc.addItems(["301", "302", "303", "304", "305"])
        elif predio == "Laboratório de elétrica / eletrônica":
            self.sala_disc.addItems(["LAB1", "LAB2", "LAB3"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sistema = SistemaAlocacao()
    sistema.show()
    sys.exit(app.exec_())
