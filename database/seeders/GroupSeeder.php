<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class GroupSeeder extends Seeder
{
    public function run()
    {
        $groups = [
            ['name' => 'Público', 'description' => 'Grupo padrão para usuários públicos'],
            ['name' => 'Turma A', 'description' => 'Turma A de alunos'],
            ['name' => 'Evento 2024', 'description' => 'Participantes do evento 2024'],
            ['name' => 'Funcionários', 'description' => 'Funcionários da escola'],
        ];

        foreach ($groups as $group) {
            DB::table('groups')->updateOrInsert(
                ['name' => $group['name']],
                ['description' => $group['description'], 'created_at' => now(), 'updated_at' => now()]
            );
        }
    }
}
