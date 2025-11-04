cat > audio-manager.sh << 'EOF'
#!/bin/bash

SERVER_DIR="/Volumes/1_Tera_ExFa/A.Server"
AUDIO_DIR="$SERVER_DIR/audio-files"

echo "AUDIO MANAGER - Server Locale"
echo "Directory: $AUDIO_DIR"
echo "======================================"

# Crea cartella audio se non esiste
mkdir -p "$AUDIO_DIR"

while true; do
    echo ""
    echo "1. Lista file audio"
    echo "2. Copia file nel server"
    echo "3. Elimina file"
    echo "4. Avvia server web"
    echo "5. Info spazio disco"
    echo "6. Esci"
    echo ""
    read -p "Scelta: " scelta

    case $scelta in
        1)
            echo ""
            echo "FILE AUDIO NEL SERVER:"
            echo "-------------------------"
            if find "$AUDIO_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.flac" \) 2>/dev/null | grep -q .; then
                find "$AUDIO_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.flac" \) | while read file; do
                    size=$(du -h "$file" | cut -f1)
                    echo "$(basename "$file") - $size"
                done
                count=$(find "$AUDIO_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.flac" \) | wc -l)
                echo ""
                echo "Totale: $count file audio"
            else
                echo "Nessun file audio trovato."
            fi
            ;;
        2)
            echo ""
            read -p "Percorso del file da copiare: " file_path
            if [ -f "$file_path" ]; then
                filename=$(basename "$file_path")
                cp "$file_path" "$AUDIO_DIR/"
                echo "File copiato: $filename"
                echo "Posizione: $AUDIO_DIR/$filename"
            else
                echo "File non trovato: $file_path"
            fi
            ;;
        3)
            echo ""
            echo "File disponibili:"
            if ls "$AUDIO_DIR"/*.mp3 "$AUDIO_DIR"/*.wav "$AUDIO_DIR"/*.m4a "$AUDIO_DIR"/*.flac 2>/dev/null; then
                ls "$AUDIO_DIR"/*.mp3 "$AUDIO_DIR"/*.wav "$AUDIO_DIR"/*.m4a "$AUDIO_DIR"/*.flac 2>/dev/null | while read file; do
                    echo "   $(basename "$file")"
                done
                read -p "Nome file da eliminare: " file_name
                if [ -f "$AUDIO_DIR/$file_name" ]; then
                    rm "$AUDIO_DIR/$file_name"
                    echo "File eliminato: $file_name"
                else
                    echo "File non trovato"
                fi
            else
                echo "Nessun file audio trovato."
            fi
            ;;
        4)
            echo ""
            echo "Avvio server web..."
            echo "Apri: http://localhost:8000"
            echo "Per fermare: Ctrl+C"
            python3 server.py
            ;;
        5)
            echo ""
            echo "INFORMAZIONI DISCO:"
            echo "---------------------"
            df -h "/Volumes/1_Tera_ExFa"
            echo ""
            echo "Spazio utilizzato audio:"
            du -sh "$AUDIO_DIR" 2>/dev/null || echo "0B"
            ;;
        6)
            echo "Arrivederci!"
            break
            ;;
        *)
            echo "Scelta non valida"
            ;;
    esac
done
EOF