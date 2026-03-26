from typing import Any


class RequirementBuilder:
    """
    Builds requirement strings for OpenMAIC from epidemiological data.
    """

    def build_dengue_training(
        self,
        data_summary: dict[str, Any],
        region: str,
        timeframe: str,
        target_audience: str = "agentes de saúde",
        num_slides: int = 8,
        num_quizzes: int = 3,
    ) -> str:
        """
        Generate a rich requirement string for dengue training.

        Args:
            data_summary: Summary statistics from DengueDataFetcher
            region: Region name (e.g., "São Paulo")
            timeframe: Time period description (e.g., "Ano 2024")
            target_audience: Target audience description
            num_slides: Number of slides to generate
            num_quizzes: Number of quiz questions to generate

        Returns:
            Formatted requirement string for OpenMAIC
        """
        total_cases = data_summary.get("total_cases", 0)
        deaths = data_summary.get("deaths", 0)
        hospitalizations = data_summary.get("hospitalizations", 0)
        fatality_rate = data_summary.get("fatality_rate", 0.0)

        weekly_table = self._format_weekly_data(data_summary.get("by_week", {}))

        requirement = f"""Crie uma aula de treinamento sobre vigilância de Dengue para {target_audience} na região {region}, usando dados reais do período {timeframe}.

## DADOS EPIDEMIOLÓGICOS REAIS

### Situação Atual
- **Total de casos notificados:** {total_cases:,}
- **Hospitalizações:** {hospitalizations:,}
- **Óbitos:** {deaths:,}
- **Taxa de letalidade:** {fatality_rate:.2f}%

### Distribuição Semanal (últimas semanas)
{weekly_table}

## OBJETIVOS DE APRENDIZAGEM
1. Compreender a situação epidemiológica atual da dengue na região {region}
2. Identificar sinais de alerta e fatores de risco para dengue grave
3. Conhecer os protocolos de investigação de casos suspeitos
4. Praticar ações de prevenção e controle vetorial

## ESTRUTURA DA AULA
- {num_slides} a {num_slides + 2} slides com dados locais e orientações práticas
- {num_quizzes} a {num_quizzes + 2} questões de quiz para fixação
- Linguagem: Português do Brasil

## PÚBLICO-ALVO
{target_audience}

## TOM E ESTILO
- Profissional mas acessível
- Use exemplos práticos do dia a dia dos agentes de saúde
- Inclua dicas práticas de campo
- Enfatize a importância da notificação oportuna

## CONTEÚDO ESPECÍFICO A INCLUIR
1. Definição de caso suspeito de dengue
2. Sinais de alarme para dengue grave
3. Fluxo de notificação no SINAN
4. Medidas de controle vetorial
5. Educação em saúde para a comunidade"""
        return requirement.strip()

    def _format_weekly_data(self, weekly: dict[int, int]) -> str:
        """
        Format weekly data as a markdown table.

        Args:
            weekly: Dictionary mapping week numbers to case counts

        Returns:
            Markdown-formatted table string
        """
        if not weekly:
            return "Dados semanais não disponíveis"

        lines = ["| Semana Epidemiológica | Casos |", "|:---------------------:|:-----:|"]

        sorted_weeks = sorted(weekly.items())
        recent_weeks = sorted_weeks[-8:] if len(sorted_weeks) > 8 else sorted_weeks

        for week, cases in recent_weeks:
            lines.append(f"| {week} | {cases:,} |")

        return "\n".join(lines)
